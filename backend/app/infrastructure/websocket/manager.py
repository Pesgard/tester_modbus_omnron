"""
WebSocket manager for real-time communication with clients.
"""
import json
import logging
from datetime import datetime
from typing import Set
from fastapi import WebSocket, WebSocketDisconnect

from ...domain.models import ProductionData
from ...core.config import settings

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manager for handling WebSocket connections in real-time."""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.max_connections = settings.websocket_max_connections
    
    async def connect(self, websocket: WebSocket):
        """Accept new WebSocket connection."""
        if len(self.active_connections) >= self.max_connections:
            await websocket.close(code=1008, reason="Maximum connections reached")
            logger.warning(f"Connection rejected: maximum connections ({self.max_connections}) reached")
            return False
        
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"New WebSocket connection. Total connected: {len(self.active_connections)}")
        return True
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection."""
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket connection closed. Total connected: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to a specific connection."""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: str):
        """Send message to all active connections."""
        if not self.active_connections:
            return
        
        disconnected = set()
        for connection in self.active_connections.copy():
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error in broadcast: {e}")
                disconnected.add(connection)
        
        # Clean up dead connections
        for conn in disconnected:
            self.disconnect(conn)
    
    async def broadcast_production_data(self, data: ProductionData):
        """Send production data to all clients."""
        message = {
            "type": "production_data",
            "data": data.to_dict(),
            "timestamp": datetime.now().isoformat()
        }
        await self.broadcast(json.dumps(message))
    
    async def send_welcome_message(self, websocket: WebSocket):
        """Send welcome message to new connection."""
        welcome_message = {
            "type": "connection",
            "message": "Connected to production system real-time monitoring",
            "timestamp": datetime.now().isoformat()
        }
        await self.send_personal_message(json.dumps(welcome_message), websocket)
    
    async def send_current_data(self, websocket: WebSocket, data: ProductionData):
        """Send current production data to specific client."""
        current_message = {
            "type": "current_data",
            "data": data.to_dict(),
            "timestamp": datetime.now().isoformat()
        }
        await self.send_personal_message(json.dumps(current_message), websocket)
    
    async def handle_client_message(self, websocket: WebSocket, message: str):
        """Handle incoming message from client."""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type == "ping":
                response = {
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                }
                await self.send_personal_message(json.dumps(response), websocket)
            else:
                logger.info(f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON received: {message}")
        except Exception as e:
            logger.error(f"Error handling client message: {e}")
    
    def get_connection_count(self) -> int:
        """Get number of active connections."""
        return len(self.active_connections)
    
    def get_connection_info(self) -> dict:
        """Get connection information."""
        return {
            "active_connections": len(self.active_connections),
            "max_connections": self.max_connections,
            "connection_rate": len(self.active_connections) / self.max_connections * 100
        } 