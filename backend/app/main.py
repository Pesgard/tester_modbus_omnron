"""
Main application orchestrator for the production system.
This file wires together all the components using dependency injection.
"""
import asyncio
import threading
import signal
import sys
from contextlib import asynccontextmanager
from queue import Queue, Empty
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Core configuration
from .core.config import settings

# Domain services
from .domain.services.production_service import ProductionService

# Infrastructure
from .infrastructure.database.repository import (
    DatabaseManager, ProductionRepository, UserRepository, 
    AuditLogRepository, SystemEventRepository, BatchIdGenerator, init_default_data
)
from .infrastructure.modbus.server import ModbusServer
from .infrastructure.websocket.manager import WebSocketManager
from .infrastructure.logging.config import setup_logging, get_logger
from .infrastructure.api.routes import all_routers

# Domain services
from .domain.services.auth_service import AuthService

# Presentation
from .presentation.web_client import get_home_page, get_realtime_client

# Setup logging first
setup_logging()
logger = get_logger(__name__)

# Global instances
db_manager: Optional[DatabaseManager] = None
production_service: Optional[ProductionService] = None
user_repository: Optional[UserRepository] = None
audit_repository: Optional[AuditLogRepository] = None
auth_service: Optional[AuthService] = None
modbus_server: Optional[ModbusServer] = None
websocket_manager: Optional[WebSocketManager] = None
data_processor: Optional['DataProcessor'] = None


class DataProcessor:
    """Processes data from Modbus and coordinates with other services."""
    
    def __init__(self, production_service: ProductionService, websocket_manager: WebSocketManager):
        self.production_service = production_service
        self.websocket_manager = websocket_manager
        self.data_buffer = Queue(maxsize=settings.data_buffer_size)
        self.processing_thread: Optional[threading.Thread] = None
        self.running = False
        self.main_loop: Optional[asyncio.AbstractEventLoop] = None
        
    def start(self):
        """Start the data processor."""
        self.running = True
        try:
            self.main_loop = asyncio.get_running_loop()
        except RuntimeError:
            self.main_loop = None
            
        self.processing_thread = threading.Thread(target=self._process_buffer)
        self.processing_thread.daemon = True
        self.processing_thread.start()
        logger.info("Data processor started")
    
    def stop(self):
        """Stop the data processor."""
        self.running = False
        if self.processing_thread:
            self.processing_thread.join(timeout=5)
            logger.info("Data processor stopped")
    
    def handle_plc_data(self, address: int, values: list):
        """Handle PLC data from Modbus server."""
        try:
            # Process data using domain service
            production_data = self.production_service.process_plc_data(address, values)
            
            if production_data:
                # Add to buffer for async processing
                try:
                    self.data_buffer.put_nowait(production_data)
                except:
                    logger.warning("Data buffer full, discarding oldest data")
                    try:
                        self.data_buffer.get_nowait()
                        self.data_buffer.put_nowait(production_data)
                    except:
                        pass
        except Exception as e:
            logger.error(f"Error handling PLC data: {e}")
    
    def _process_buffer(self):
        """Process data buffer in background thread."""
        while self.running:
            try:
                data = self.data_buffer.get(timeout=1)
                
                # Save to database
                success = self.production_service.save_production_data(data)
                
                if success:
                    logger.info(f"Data processed: Product {data.product_id}, Quality: {data.quality_status.name}")
                    # Send via WebSocket
                    self._send_websocket_data(data)
                else:
                    logger.error("Error saving data to database")
                    
            except Empty:
                continue
            except Exception as e:
                logger.error(f"Error in data processing buffer: {e}")
    
    def _send_websocket_data(self, data):
        """Send data via WebSocket in thread-safe manner."""
        try:
            if self.main_loop is not None:
                future = asyncio.run_coroutine_threadsafe(
                    self.websocket_manager.broadcast_production_data(data),
                    self.main_loop
                )
                # Don't wait for result to avoid blocking
            else:
                logger.warning("No main event loop found for WebSocket")
        except Exception as e:
            logger.error(f"Error sending WebSocket data: {e}")


def get_production_service_instance() -> ProductionService:
    """Get the global production service instance."""
    if production_service is None:
        raise RuntimeError("Production service not initialized")
    return production_service


def get_auth_service() -> AuthService:
    """Get the global auth service instance."""
    if auth_service is None:
        raise RuntimeError("Auth service not initialized")
    return auth_service


def get_user_repository() -> UserRepository:
    """Get the global user repository instance."""
    if user_repository is None:
        raise RuntimeError("User repository not initialized")
    return user_repository


async def setup_dependencies():
    """Setup all dependencies and wire them together."""
    global db_manager, production_service, user_repository, audit_repository, auth_service
    global modbus_server, websocket_manager, data_processor
    
    logger.info("Setting up application dependencies...")
    
    # Database layer
    db_manager = DatabaseManager()
    await db_manager.create_tables()
    
    # Repositories
    production_repository = ProductionRepository(db_manager)
    user_repository = UserRepository(db_manager)
    audit_repository = AuditLogRepository(db_manager)
    batch_generator = BatchIdGenerator()
    
    # Initialize default data
    await init_default_data(db_manager)
    
    # Domain services
    # Note: We'll need to update ProductionService to handle async repository
    # For now, we'll create a sync wrapper or update the service
    production_service = ProductionService(production_repository, batch_generator)
    auth_service = AuthService(user_repository, audit_repository)
    
    # Infrastructure services
    websocket_manager = WebSocketManager()
    data_processor = DataProcessor(production_service, websocket_manager)
    modbus_server = ModbusServer(data_processor.handle_plc_data)
    
    logger.info("Dependencies setup complete")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    # Startup
    logger.info("Starting production system services...")
    
    await setup_dependencies()
    
    # Start data processor
    if data_processor:
        data_processor.start()
    
    # Start Modbus server in background
    modbus_task = None
    if modbus_server:
        modbus_task = asyncio.create_task(modbus_server.start())
    
    logger.info("All services started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down production system services...")
    
    # Stop data processor
    if data_processor:
        data_processor.stop()
    
    # Stop Modbus server
    if modbus_server:
        modbus_server.stop()
    
    if modbus_task:
        modbus_task.cancel()
        try:
            await modbus_task
        except asyncio.CancelledError:
            pass
    
    logger.info("All services stopped")


# Create FastAPI app with comprehensive metadata
app = FastAPI(
    title="🏭 Production System API",
    description="""
    ## Industrial Production Monitoring and Control System
    
    This comprehensive API provides real-time monitoring and control capabilities for industrial production lines.
    
    ### Key Features:
    
    * 🔧 **Modbus TCP Integration**: Direct communication with PLCs and industrial equipment
    * 📊 **Real-time Data Processing**: Live production data collection and analysis
    * 🌐 **WebSocket Support**: Real-time data streaming to connected clients
    * 🔐 **JWT Authentication**: Secure access with role-based permissions
    * 📈 **Production Analytics**: Statistical analysis and reporting
    * 🗄️ **PostgreSQL Storage**: Persistent data storage with full audit trail
    
    ### Authentication:
    
    Most endpoints require authentication. Use the `/api/auth/login` endpoint to obtain a JWT token.
    
    ### Data Flow:
    
    1. **PLC Data Collection**: Modbus server receives data from industrial equipment
    2. **Processing**: Data is validated, transformed, and stored
    3. **Real-time Broadcasting**: WebSocket clients receive live updates
    4. **Analytics**: Statistical analysis and quality monitoring
    
    ### Roles:
    
    - **Admin**: Full system access including user management
    - **Supervisor**: Production oversight and reporting
    - **Operator**: Basic production monitoring and control
    - **Viewer**: Read-only access to production data
    """,
    version=settings.api_version,
    contact={
        "name": "Production System Support",
        "url": "https://github.com/company/production-system",
        "email": "support@company.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    terms_of_service="https://company.com/terms/",
    openapi_tags=[
        {
            "name": "authentication",
            "description": "User authentication and authorization operations. Login to get JWT tokens."
        },
        {
            "name": "production",
            "description": "Production data operations. Monitor and analyze manufacturing processes."
        },
        {
            "name": "system",
            "description": "System health and diagnostic operations. Monitor API and infrastructure status."
        },
        {
            "name": "administration",
            "description": "Administrative operations. User management and system configuration. **Admin access required**."
        }
    ],
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
for router in all_routers:
    app.include_router(router)

# Web presentation routes
@app.get("/", 
         summary="Home Page",
         description="Returns the main dashboard page with navigation to all system features.",
         tags=["web-interface"])
async def read_root():
    """
    ## Home Page
    
    Returns the main dashboard page for the production system.
    
    **Features:**
    - System overview
    - Quick navigation to monitoring tools
    - Status indicators
    """
    return get_home_page()

@app.get("/client", 
         summary="Real-time Monitoring Client",
         description="Returns the WebSocket-based real-time monitoring interface.",
         tags=["web-interface"])
async def realtime_client():
    """
    ## Real-time Production Monitor
    
    Interactive web client for monitoring production data in real-time.
    
    **Features:**
    - Live production data display
    - WebSocket connection status
    - Interactive charts and metrics
    - System diagnostics
    """
    return get_realtime_client()

@app.websocket("/ws/production")
async def websocket_endpoint(websocket: WebSocket):
    """
    ## Production Data WebSocket
    
    WebSocket endpoint for real-time production data streaming.
    
    **Connection URL:** `ws://localhost:8000/ws/production`
    
    **Message Types Sent:**
    - `connection`: Connection confirmation
    - `production_data`: Real-time production data
    - `pong`: Response to client ping
    
    **Message Types Received:**
    - `ping`: Heartbeat from client
    
    **Example Client Code:**
    ```javascript
    const socket = new WebSocket('ws://localhost:8000/ws/production');
    socket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        console.log('Production data:', data);
    };
    ```
    """
    if websocket_manager:
        await websocket_manager.connect(websocket)
        try:
            while True:
                data = await websocket.receive_text()
                message = {"type": "pong", "timestamp": str(asyncio.get_event_loop().time())}
                await websocket.send_text(str(message))
        except WebSocketDisconnect:
            websocket_manager.disconnect(websocket)


def main():
    """Run the production system application."""
    
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info(f"Starting {settings.api_title} v{settings.api_version}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"API will be available at: http://{settings.api_host}:{settings.api_port}")
    logger.info(f"API documentation: http://{settings.api_host}:{settings.api_port}/docs")
    logger.info(f"Alternative docs: http://{settings.api_host}:{settings.api_port}/redoc")
    
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )


if __name__ == "__main__":
    main() 