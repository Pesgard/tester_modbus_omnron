import asyncio
import sqlite3
import threading
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from contextlib import contextmanager
from queue import Queue, Empty
import signal
import sys

# FastAPI para REST API escalable
from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from contextlib import asynccontextmanager
import uvicorn

# Pymodbus para servidor Modbus
from pymodbus.server import StartAsyncTcpServer
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.device import ModbusDeviceIdentification

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('production_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# Enums y DataClasses
class ProductionStatus(Enum):
    STOPPED = 0
    RUNNING = 1
    ERROR = 2
    MAINTENANCE = 3


class QualityStatus(Enum):
    NOK = 0
    OK = 1
    PENDING = 2


@dataclass
class ProductionData:
    timestamp: datetime
    product_id: int
    quality_status: QualityStatus
    production_count: int
    line_status: ProductionStatus
    error_code: int
    cycle_time_ms: int
    temperature: float
    pressure: float
    operator_id: int
    batch_id: str

    def to_dict(self) -> Dict:
        """Convertir a diccionario para JSON"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['quality_status'] = self.quality_status.value
        data['line_status'] = self.line_status.value
        return data


class WebSocketManager:
    """Manager para manejar conexiones WebSocket en tiempo real"""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        """Aceptar nueva conexión WebSocket"""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"Nueva conexión WebSocket. Total conectados: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Remover conexión WebSocket"""
        self.active_connections.discard(websocket)
        logger.info(f"Conexión WebSocket cerrada. Total conectados: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Enviar mensaje a una conexión específica"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error enviando mensaje personal: {e}")
            self.disconnect(websocket)

    async def broadcast(self, message: str):
        """Enviar mensaje a todas las conexiones activas"""
        if not self.active_connections:
            return

        disconnected = set()
        for connection in self.active_connections.copy():
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error en broadcast: {e}")
                disconnected.add(connection)

        # Limpiar conexiones muertas
        for conn in disconnected:
            self.disconnect(conn)

    async def broadcast_production_data(self, data: ProductionData):
        """Enviar datos de producción a todos los clientes"""
        message = {
            "type": "production_data",
            "data": data.to_dict(),
            "timestamp": datetime.now().isoformat()
        }
        await self.broadcast(json.dumps(message))


# Instancia global del manager de WebSocket
websocket_manager = WebSocketManager()


class ProductionDataBlock(ModbusSequentialDataBlock):
    """Bloque Modbus personalizado que captura escrituras del PLC"""

    def __init__(self, address: int, values: List[int], data_processor):
        super().__init__(address, values)
        self.data_processor = data_processor
        self.last_update = time.time()

    def setValues(self, address: int, values: List[int]) -> None:
        """Captura cuando el PLC escribe datos"""
        try:
            old_values = self.getValues(address, len(values))
            super().setValues(address, values)

            # Solo procesar si hay cambios reales
            if old_values != values:
                self.data_processor.process_plc_data(address, values)
                self.last_update = time.time()
                
                # Logging más detallado
                if address in [0, 1]:
                    logger.info(f"📡 PLC escribió DATOS PRINCIPALES en dirección {address}: {values[:10]}")
                elif address in [20, 21]:
                    logger.info(f"📊 PLC escribió DATOS CALIDAD en dirección {address}: {values[:5]}")
                elif address in [40, 41]:
                    logger.info(f"🌡️ PLC escribió DATOS PROCESO en dirección {address}: Temp={values[0]/10}°C, Press={values[2]/10}bar")
                else:
                    logger.info(f"📝 PLC escribió en dirección {address}: {values}")

        except Exception as e:
            logger.error(f"Error procesando datos del PLC: {e}")


class DatabaseManager:
    """Gestor de base de datos con pool de conexiones"""

    def __init__(self, db_path: str = "production_system.db"):
        self.db_path = db_path
        self.connection_pool = Queue(maxsize=10)
        self.setup_database()
        self._init_connection_pool()

    def _init_connection_pool(self):
        """Inicializar pool de conexiones"""
        for _ in range(5):  # 5 conexiones iniciales
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA cache_size=10000")
            self.connection_pool.put(conn)

    @contextmanager
    def get_connection(self):
        """Context manager para obtener conexión del pool"""
        conn = None
        try:
            conn = self.connection_pool.get(timeout=5)
            yield conn
        except Empty:
            # Si no hay conexiones disponibles, crear una nueva
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.execute("PRAGMA journal_mode=WAL")
            yield conn
        finally:
            if conn:
                try:
                    self.connection_pool.put_nowait(conn)
                except:
                    conn.close()

    def setup_database(self):
        """Configurar esquema de base de datos"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA journal_mode=WAL")

            # Tabla principal de producción
            conn.execute('''
                CREATE TABLE IF NOT EXISTS production_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    product_id INTEGER,
                    quality_status INTEGER,
                    production_count INTEGER,
                    line_status INTEGER,
                    error_code INTEGER,
                    cycle_time_ms INTEGER,
                    temperature REAL,
                    pressure REAL,
                    operator_id INTEGER,
                    batch_id TEXT,
                    shift_id TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Tabla de alertas y eventos
            conn.execute('''
                CREATE TABLE IF NOT EXISTS system_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    event_type TEXT,
                    severity TEXT,
                    message TEXT,
                    source TEXT,
                    resolved BOOLEAN DEFAULT FALSE
                )
            ''')

            # Tabla de configuración
            conn.execute('''
                CREATE TABLE IF NOT EXISTS system_config (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    description TEXT,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Índices para mejor performance
            conn.execute('CREATE INDEX IF NOT EXISTS idx_production_timestamp ON production_data(timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_production_batch ON production_data(batch_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_events_timestamp ON system_events(timestamp)')

            conn.commit()
            logger.info("Base de datos configurada correctamente")

    def insert_production_data(self, data: ProductionData) -> bool:
        """Insertar datos de producción"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO production_data 
                    (timestamp, product_id, quality_status, production_count, 
                     line_status, error_code, cycle_time_ms, temperature, 
                     pressure, operator_id, batch_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    data.timestamp, data.product_id, data.quality_status.value,
                    data.production_count, data.line_status.value, data.error_code,
                    data.cycle_time_ms, data.temperature, data.pressure,
                    data.operator_id, data.batch_id
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error insertando datos de producción: {e}")
            return False

    def get_production_data(self, start_date: Optional[datetime] = None,
                            end_date: Optional[datetime] = None, limit: int = 1000) -> List[Dict]:
        """Obtener datos de producción con filtros"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                query = "SELECT * FROM production_data"
                params = []

                conditions = []
                if start_date:
                    conditions.append("timestamp >= ?")
                    params.append(start_date)
                if end_date:
                    conditions.append("timestamp <= ?")
                    params.append(end_date)

                if conditions:
                    query += " WHERE " + " AND ".join(conditions)

                query += " ORDER BY timestamp DESC LIMIT ?"
                params.append(limit)

                cursor.execute(query, params)
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error obteniendo datos de producción: {e}")
            return []


class DataProcessor:
    """Procesador de datos del PLC con buffer y validación"""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.data_buffer = Queue(maxsize=1000)
        self.processing_thread = None
        self.running = False
        self.current_batch = self._generate_batch_id()
        # Buffer para almacenar datos de diferentes direcciones
        self.register_cache = {}
        # Referencia al event loop principal para WebSocket
        self.main_loop = None

    def start(self):
        """Iniciar procesamiento en segundo plano"""
        self.running = True
        # Obtener referencia al event loop actual
        try:
            self.main_loop = asyncio.get_running_loop()
        except RuntimeError:
            self.main_loop = None
        
        self.processing_thread = threading.Thread(target=self._process_buffer)
        self.processing_thread.daemon = True
        self.processing_thread.start()
        logger.info("Procesador de datos iniciado")

    def stop(self):
        """Detener procesamiento"""
        self.running = False
        if self.processing_thread:
            self.processing_thread.join(timeout=5)

    def _generate_batch_id(self) -> str:
        """Generar ID de lote basado en fecha/hora"""
        return f"BATCH_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    def process_plc_data(self, address: int, values: List[int]):
        """Procesar datos recibidos del PLC"""
        try:
            # Almacenar datos en caché por dirección
            self.register_cache[address] = values
            
            # Procesar según la dirección de escritura
            if address == 0:  # Dirección original (mantener compatibilidad)
                self._process_address_0(values)
            elif address == 1:  # Datos principales desde cliente PLC nuevo
                self._process_address_1(values)
            elif address in [20, 21]:  # Datos de calidad detallados
                self._process_address_quality(address, values)
            elif address in [40, 41]:  # Datos de proceso
                self._process_address_process(address, values)

        except Exception as e:
            logger.error(f"Error procesando datos del PLC: {e}")

    def _process_address_0(self, values: List[int]):
        """Procesar datos de dirección 0 (formato original)"""
        if len(values) >= 10:
            production_data = ProductionData(
                timestamp=datetime.now(),
                product_id=values[0],
                quality_status=QualityStatus(values[1]),
                production_count=values[2],
                line_status=ProductionStatus(values[3]),
                error_code=values[4],
                cycle_time_ms=values[5],
                temperature=values[6] / 10.0,
                pressure=values[7] / 10.0,
                operator_id=values[8],
                batch_id=self.current_batch
            )
            self._add_to_buffer(production_data)

    def _process_address_1(self, values: List[int]):
        """Procesar registros principales del nuevo cliente PLC (dirección 1)"""
        if len(values) >= 10:
            # Mapeo según el cliente PLC:
            # 0: product_id, 1: quality_status, 2: production_count, 
            # 3: ok_count, 4: nok_count, 5: line_status, 6: error_code,
            # 7: cycle_time, 8: operator_id, 9: station_id
            
            production_data = ProductionData(
                timestamp=datetime.now(),
                product_id=values[0],
                quality_status=QualityStatus(values[1]),
                production_count=values[2],
                line_status=ProductionStatus(values[5]),  # line_status está en posición 5
                error_code=values[6],
                cycle_time_ms=values[7],
                # Obtener temperatura y presión de registros de proceso si están disponibles
                temperature=self._get_temperature_from_cache(),
                pressure=self._get_pressure_from_cache(),
                operator_id=values[8],
                batch_id=self.current_batch
            )
            self._add_to_buffer(production_data)

    def _process_address_quality(self, address: int, values: List[int]):
        """Procesar registros de calidad detallados (direcciones 20-21)"""
        # Los datos de calidad se almacenan en caché para usarse con los datos principales
        logger.debug(f"Datos de calidad recibidos en dirección {address}: {values}")

    def _process_address_process(self, address: int, values: List[int]):
        """Procesar registros de proceso (direcciones 40-41)"""
        # Los datos de proceso se almacenan en caché para usarse con los datos principales
        logger.debug(f"Datos de proceso recibidos en dirección {address}: {values}")

    def _get_temperature_from_cache(self) -> float:
        """Obtener temperatura de los registros de proceso"""
        process_regs = self.register_cache.get(40) or self.register_cache.get(41)
        if process_regs and len(process_regs) > 0:
            return process_regs[0] / 10.0  # Temperatura está en posición 0, dividir por 10
        return 25.0  # Valor por defecto

    def _get_pressure_from_cache(self) -> float:
        """Obtener presión de los registros de proceso"""
        process_regs = self.register_cache.get(40) or self.register_cache.get(41)
        if process_regs and len(process_regs) > 2:
            return process_regs[2] / 10.0  # Presión hidráulica está en posición 2, dividir por 10
        return 4.0  # Valor por defecto

    def _add_to_buffer(self, production_data: ProductionData):
        """Agregar datos al buffer para procesamiento asíncrono"""
        try:
            self.data_buffer.put_nowait(production_data)
        except:
            logger.warning("Buffer lleno, descartando datos más antiguos")
            try:
                self.data_buffer.get_nowait()  # Remover el más antiguo
                self.data_buffer.put_nowait(production_data)
            except:
                pass

    def _process_buffer(self):
        """Procesar buffer de datos en segundo plano"""
        while self.running:
            try:
                data = self.data_buffer.get(timeout=1)
                success = self.db_manager.insert_production_data(data)
                if success:
                    logger.info(f"Datos procesados: Producto {data.product_id}, Calidad: {data.quality_status.name}")
                    # Enviar datos en tiempo real via WebSocket usando un método thread-safe
                    self._send_websocket_data(data)
                else:
                    logger.error("Error guardando en BD")
            except Empty:
                continue
            except Exception as e:
                logger.error(f"Error en procesamiento de buffer: {e}")

    def _send_websocket_data(self, data: ProductionData):
        """Enviar datos via WebSocket de forma thread-safe"""
        try:
            if self.main_loop is not None:
                # Programar tarea en el event loop principal
                future = asyncio.run_coroutine_threadsafe(
                    websocket_manager.broadcast_production_data(data),
                    self.main_loop
                )
                # No esperar el resultado para no bloquear
            else:
                logger.warning("No se encontró event loop principal para WebSocket")
                
        except Exception as e:
            logger.error(f"Error configurando envío WebSocket: {e}")


class ProductionModbusServer:
    """Servidor Modbus principal"""

    def __init__(self, host: str = "0.0.0.0", port: int = 502):
        self.host = host
        self.port = port
        self.db_manager = DatabaseManager()
        self.data_processor = DataProcessor(self.db_manager)
        self.server_task = None

    async def start_server(self):
        """Iniciar servidor Modbus"""
        try:
            # Crear bloques de datos con procesador personalizado
            # Expandir el bloque para cubrir direcciones 0-100 (incluye 1, 21, 41 que usa el cliente)
            store = ModbusSlaveContext(
                di=ModbusSequentialDataBlock(0, [0] * 200),  # Discrete Inputs
                co=ModbusSequentialDataBlock(0, [0] * 200),  # Coils
                hr=ProductionDataBlock(0, [0] * 200, self.data_processor),  # Holding Registers (0-199)
                ir=ModbusSequentialDataBlock(0, [0] * 200)  # Input Registers
            )

            context = ModbusServerContext(slaves=store, single=True)

            # Identidad del dispositivo
            identity = ModbusDeviceIdentification()
            identity.VendorName = 'Production System'
            identity.ProductCode = 'PS'
            identity.VendorUrl = 'http://localhost'
            identity.ProductName = 'Production Modbus Server'
            identity.ModelName = 'Production Server v2.0'
            identity.MajorMinorRevision = '2.0'

            # Iniciar procesador de datos
            self.data_processor.start()

            # Iniciar servidor
            logger.info(f"Iniciando servidor Modbus en {self.host}:{self.port}")
            logger.info("Servidor configurado para recibir datos en direcciones 0-199")
            logger.info("Direcciones esperadas del PLC: 1 (principales), 21 (calidad), 41 (proceso)")
            self.server_task = asyncio.create_task(
                StartAsyncTcpServer(
                    context=context,
                    identity=identity,
                    address=(self.host, self.port)
                )
            )

            await self.server_task

        except Exception as e:
            logger.error(f"Error iniciando servidor Modbus: {e}")
            raise

    def stop_server(self):
        """Detener servidor"""
        if self.server_task:
            self.server_task.cancel()
        self.data_processor.stop()


# Instancia global del servidor
modbus_server = ProductionModbusServer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manejar el ciclo de vida de la aplicación"""
    # Startup
    logger.info("Iniciando servicios del sistema de producción")
    # Iniciar servidor Modbus en background
    modbus_task = asyncio.create_task(modbus_server.start_server())
    yield
    # Shutdown
    logger.info("Cerrando servicios del sistema de producción")
    modbus_server.stop_server()
    if modbus_task:
        modbus_task.cancel()
        try:
            await modbus_task
        except asyncio.CancelledError:
            pass


# FastAPI REST API
app = FastAPI(
    title="Production System API",
    description="API para sistema de producción con Modbus",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Endpoints REST API
@app.get("/api/production/current")
async def get_current_production():
    """Obtener estado actual de producción"""
    try:
        data = modbus_server.db_manager.get_production_data(limit=1)
        if data:
            return {"status": "success", "data": data[0]}
        return {"status": "success", "data": None}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/production/history")
async def get_production_history(
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100
):
    """Obtener historial de producción"""
    try:
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None

        data = modbus_server.db_manager.get_production_data(
            start_date=start_dt,
            end_date=end_dt,
            limit=limit
        )

        return {"status": "success", "data": data, "count": len(data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/production/stats")
async def get_production_stats():
    """Obtener estadísticas de producción"""
    try:
        # Estadísticas del día actual
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        data = modbus_server.db_manager.get_production_data(
            start_date=today,
            limit=10000
        )

        total_products = len(data)
        quality_ok = len([d for d in data if d.get('quality_status') == 1])
        quality_rate = (quality_ok / total_products * 100) if total_products > 0 else 0

        return {
            "status": "success",
            "stats": {
                "total_products_today": total_products,
                "quality_ok_today": quality_ok,
                "quality_rate_today": round(quality_rate, 2),
                "last_update": datetime.now().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/system/health")
async def health_check():
    """Health check del sistema"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "modbus_server": "running",
            "database": "connected",
            "api": "running"
        },
        "connected_clients": len(websocket_manager.active_connections)
    }


@app.get("/api/debug/recent-data")
async def get_recent_debug_data():
    """Endpoint de diagnóstico para ver datos recientes y estado del sistema"""
    try:
        # Obtener datos más recientes
        recent_data = modbus_server.db_manager.get_production_data(limit=5)
        
        # Información del procesador de datos
        processor_info = {
            "running": modbus_server.data_processor.running,
            "buffer_size": modbus_server.data_processor.data_buffer.qsize(),
            "current_batch": modbus_server.data_processor.current_batch,
            "register_cache_keys": list(modbus_server.data_processor.register_cache.keys()),
            "last_cache_update": max([
                time.time() - (max([
                    getattr(modbus_server.data_processor, 'last_update', 0)
                ]) or 0)
            ], default=0)
        }
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "recent_data": recent_data,
            "processor_info": processor_info,
            "websocket_connections": len(websocket_manager.active_connections),
            "total_records": len(recent_data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en diagnóstico: {str(e)}")


@app.get("/")
async def read_root():
    """Página principal - redirigir al cliente web"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sistema de Producción</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #f5f5f5; }
            .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #333; margin-bottom: 20px; }
            .btn { background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 10px; display: inline-block; }
            .btn:hover { background: #5a6fd8; }
            .info { background: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏭 Sistema de Producción Modbus</h1>
            <div class="info">
                <p>Sistema de monitoreo en tiempo real para datos de producción via Modbus TCP</p>
            </div>
            <a href="/client" class="btn">🖥️ Abrir Monitor en Tiempo Real</a>
            <a href="/docs" class="btn">📚 Documentación API</a>
            <a href="/api/system/health" class="btn">💚 Estado del Sistema</a>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/client")
async def realtime_client():
    """Cliente web para monitoreo en tiempo real"""
    html_content = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sistema de Producción - Tiempo Real</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }
        .status-panel {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
        }
        .connection-status {
            padding: 10px 20px;
            border-radius: 5px;
            color: white;
            font-weight: bold;
            text-align: center;
            margin-bottom: 20px;
        }
        .connected { background-color: #4CAF50; }
        .disconnected { background-color: #f44336; }
        .connecting { background-color: #ff9800; }

        .data-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
            margin-top: 15px;
        }
        .data-item {
            background: #f8f9fa;
            padding: 10px;
            border-radius: 5px;
            border-left: 3px solid #28a745;
        }
        .data-label {
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
            font-weight: bold;
        }
        .data-value {
            font-size: 18px;
            font-weight: bold;
            color: #333;
            margin-top: 2px;
        }

        .quality-ok { color: #28a745; }
        .quality-nok { color: #dc3545; }
        .quality-pending { color: #ffc107; }

        .status-running { color: #28a745; }
        .status-stopped { color: #dc3545; }
        .status-error { color: #fd7e14; }
        .status-maintenance { color: #6f42c1; }

        .log-container {
            background: #1e1e1e;
            color: #00ff00;
            padding: 15px;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            height: 200px;
            overflow-y: auto;
            margin-top: 20px;
        }

        .controls {
            text-align: center;
            margin: 20px 0;
        }
        .btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin: 0 5px;
            font-size: 14px;
        }
        .btn:hover {
            background: #5a6fd8;
        }
        .btn:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏭 Sistema de Producción - Monitor en Tiempo Real</h1>
            <p>Monitoreo de datos desde el servidor Modbus</p>
        </div>

        <div id="connectionStatus" class="connection-status connecting">
            🔄 Conectando al servidor...
        </div>

        <div class="controls">
            <button id="connectBtn" class="btn" onclick="connect()">Conectar</button>
            <button id="disconnectBtn" class="btn" onclick="disconnect()" disabled>Desconectar</button>
            <button class="btn" onclick="clearLog()">Limpiar Log</button>
            <button class="btn" onclick="sendPing()">Ping</button>
            <button class="btn" onclick="checkRecentData()">🔍 Diagnóstico</button>
        </div>

        <div class="status-panel">
            <div class="card">
                <h3>📊 Datos de Producción Actuales</h3>
                <div id="productionData" class="data-grid">
                    <div class="data-item">
                        <div class="data-label">Estado</div>
                        <div class="data-value">Esperando datos...</div>
                    </div>
                </div>
            </div>

            <div class="card">
                <h3>📈 Estadísticas de Sesión</h3>
                <div class="data-grid">
                    <div class="data-item">
                        <div class="data-label">Mensajes Recibidos</div>
                        <div class="data-value" id="messageCount">0</div>
                    </div>
                    <div class="data-item">
                        <div class="data-label">Productos Procesados</div>
                        <div class="data-value" id="productCount">0</div>
                    </div>
                    <div class="data-item">
                        <div class="data-label">Tiempo Conectado</div>
                        <div class="data-value" id="connectionTime">00:00:00</div>
                    </div>
                </div>
            </div>
        </div>

        <div class="card">
            <h3>📝 Log de Eventos</h3>
            <div id="log" class="log-container"></div>
        </div>
    </div>

    <script>
        let socket = null;
        let messageCount = 0;
        let productCount = 0;
        let connectionStartTime = null;
        let connectionTimer = null;

        const statusMapping = {
            0: { text: 'Detenido', class: 'status-stopped' },
            1: { text: 'En Funcionamiento', class: 'status-running' },
            2: { text: 'Error', class: 'status-error' },
            3: { text: 'Mantenimiento', class: 'status-maintenance' }
        };

        const qualityMapping = {
            0: { text: 'NOK', class: 'quality-nok' },
            1: { text: 'OK', class: 'quality-ok' },
            2: { text: 'Pendiente', class: 'quality-pending' }
        };

        function addLog(message, type = 'info') {
            const log = document.getElementById('log');
            const timestamp = new Date().toLocaleTimeString();
            const colorMap = {
                'info': '#00ff00',
                'warning': '#ffff00',
                'error': '#ff0000',
                'success': '#00ffff'
            };

            log.innerHTML += `<div style="color: ${colorMap[type] || '#00ff00'}">[${timestamp}] ${message}</div>`;
            log.scrollTop = log.scrollHeight;
        }

        function updateConnectionStatus(status, message) {
            const statusEl = document.getElementById('connectionStatus');
            statusEl.className = `connection-status ${status}`;

            const statusText = {
                'connected': '✅ Conectado al servidor',
                'disconnected': '❌ Desconectado del servidor',
                'connecting': '🔄 Conectando al servidor...'
            };

            statusEl.textContent = statusText[status] || message;
        }

        function updateConnectionTime() {
            if (connectionStartTime) {
                const elapsed = Date.now() - connectionStartTime;
                const hours = Math.floor(elapsed / 3600000);
                const minutes = Math.floor((elapsed % 3600000) / 60000);
                const seconds = Math.floor((elapsed % 60000) / 1000);

                document.getElementById('connectionTime').textContent = 
                    `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            }
        }

        function connect() {
            if (socket && socket.readyState === WebSocket.OPEN) {
                addLog('Ya existe una conexión activa', 'warning');
                return;
            }

            updateConnectionStatus('connecting');
            addLog('Intentando conectar al servidor WebSocket...', 'info');

            socket = new WebSocket('ws://localhost:8000/ws/production');

            socket.onopen = function(event) {
                updateConnectionStatus('connected');
                addLog('✅ Conexión WebSocket establecida', 'success');
                connectionStartTime = Date.now();
                connectionTimer = setInterval(updateConnectionTime, 1000);

                document.getElementById('connectBtn').disabled = true;
                document.getElementById('disconnectBtn').disabled = false;
            };

            socket.onmessage = function(event) {
                messageCount++;
                document.getElementById('messageCount').textContent = messageCount;

                try {
                    const data = JSON.parse(event.data);
                    handleMessage(data);
                } catch (e) {
                    addLog(`Error parseando mensaje: ${e}`, 'error');
                }
            };

            socket.onclose = function(event) {
                updateConnectionStatus('disconnected');
                addLog(`❌ Conexión cerrada. Código: ${event.code}`, 'warning');

                if (connectionTimer) {
                    clearInterval(connectionTimer);
                    connectionTimer = null;
                }

                document.getElementById('connectBtn').disabled = false;
                document.getElementById('disconnectBtn').disabled = true;
            };

            socket.onerror = function(error) {
                addLog(`❌ Error en WebSocket: ${error}`, 'error');
                updateConnectionStatus('disconnected', 'Error de conexión');
            };
        }

        function disconnect() {
            if (socket) {
                socket.close();
                socket = null;
            }
        }

        function sendPing() {
            if (socket && socket.readyState === WebSocket.OPEN) {
                const ping = { type: 'ping', timestamp: new Date().toISOString() };
                socket.send(JSON.stringify(ping));
                addLog('📡 Ping enviado', 'info');
            } else {
                addLog('❌ No hay conexión activa para enviar ping', 'error');
            }
        }

        function clearLog() {
            document.getElementById('log').innerHTML = '';
        }

        async function checkRecentData() {
            addLog('🔍 Verificando datos recientes...', 'info');
            try {
                const response = await fetch('/api/debug/recent-data');
                const data = await response.json();
                
                if (data.status === 'success') {
                    addLog(`✅ Diagnóstico exitoso:`, 'success');
                    addLog(`📊 Registros recientes: ${data.total_records}`, 'info');
                    addLog(`🔧 Procesador funcionando: ${data.processor_info.running}`, 'info');
                    addLog(`📦 Buffer size: ${data.processor_info.buffer_size}`, 'info');
                    addLog(`🔗 Conexiones WebSocket: ${data.websocket_connections}`, 'info');
                    addLog(`📝 Direcciones en caché: [${data.processor_info.register_cache_keys.join(', ')}]`, 'info');
                    
                    if (data.recent_data && data.recent_data.length > 0) {
                        const latest = data.recent_data[0];
                        addLog(`🆕 Último registro: Producto ${latest.product_id}, Calidad ${latest.quality_status}`, 'success');
                        addLog(`⏰ Timestamp: ${latest.timestamp}`, 'info');
                    } else {
                        addLog('⚠️ No hay datos recientes en la base de datos', 'warning');
                    }
                } else {
                    addLog(`❌ Error en diagnóstico: ${data.error}`, 'error');
                }
            } catch (error) {
                addLog(`❌ Error conectando con API: ${error}`, 'error');
            }
        }

        function handleMessage(data) {
            switch (data.type) {
                case 'connection':
                    addLog(`🔗 ${data.message}`, 'success');
                    break;

                case 'production_data':
                    productCount++;
                    document.getElementById('productCount').textContent = productCount;
                    updateProductionData(data.data);
                    addLog(`📦 Producto procesado: ID ${data.data.product_id}`, 'info');
                    break;

                case 'current_data':
                    updateProductionData(data.data);
                    addLog('📊 Datos actuales recibidos', 'info');
                    break;

                case 'pong':
                    addLog('📡 Pong recibido', 'success');
                    break;

                default:
                    addLog(`📨 Mensaje recibido: ${JSON.stringify(data)}`, 'info');
            }
        }

        function updateProductionData(data) {
            const container = document.getElementById('productionData');

            const qualityInfo = qualityMapping[data.quality_status] || { text: 'Desconocido', class: '' };
            const statusInfo = statusMapping[data.line_status] || { text: 'Desconocido', class: '' };

            container.innerHTML = `
                <div class="data-item">
                    <div class="data-label">ID Producto</div>
                    <div class="data-value">${data.product_id}</div>
                </div>
                <div class="data-item">
                    <div class="data-label">Calidad</div>
                    <div class="data-value ${qualityInfo.class}">${qualityInfo.text}</div>
                </div>
                <div class="data-item">
                    <div class="data-label">Contador Producción</div>
                    <div class="data-value">${data.production_count}</div>
                </div>
                <div class="data-item">
                    <div class="data-label">Estado Línea</div>
                    <div class="data-value ${statusInfo.class}">${statusInfo.text}</div>
                </div>
                <div class="data-item">
                    <div class="data-label">Código Error</div>
                    <div class="data-value">${data.error_code}</div>
                </div>
                <div class="data-item">
                    <div class="data-label">Tiempo Ciclo</div>
                    <div class="data-value">${data.cycle_time_ms} ms</div>
                </div>
                <div class="data-item">
                    <div class="data-label">Temperatura</div>
                    <div class="data-value">${data.temperature}°C</div>
                </div>
                <div class="data-item">
                    <div class="data-label">Presión</div>
                    <div class="data-value">${data.pressure} bar</div>
                </div>
                <div class="data-item">
                    <div class="data-label">ID Operador</div>
                    <div class="data-value">${data.operator_id}</div>
                </div>
                <div class="data-item">
                    <div class="data-label">ID Lote</div>
                    <div class="data-value">${data.batch_id}</div>
                </div>
                <div class="data-item">
                    <div class="data-label">Última Actualización</div>
                    <div class="data-value">${new Date(data.timestamp).toLocaleTimeString()}</div>
                </div>
            `;
        }

        // Auto-conectar al cargar la página
        window.onload = function() {
            addLog('🚀 Aplicación iniciada', 'success');
            connect();
        };

        // Manejar cierre de ventana
        window.onbeforeunload = function() {
            if (socket) {
                socket.close();
            }
        };
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)


@app.websocket("/ws/production")
async def websocket_endpoint(websocket: WebSocket):
    """Endpoint WebSocket para recibir datos de producción en tiempo real"""
    await websocket_manager.connect(websocket)

    # Enviar mensaje de bienvenida
    welcome_message = {
        "type": "connection",
        "message": "Conectado al sistema de producción en tiempo real",
        "timestamp": datetime.now().isoformat()
    }
    await websocket_manager.send_personal_message(json.dumps(welcome_message), websocket)

    # Enviar datos actuales al conectarse
    try:
        current_data = modbus_server.db_manager.get_production_data(limit=1)
        if current_data:
            current_message = {
                "type": "current_data",
                "data": current_data[0],
                "timestamp": datetime.now().isoformat()
            }
            await websocket_manager.send_personal_message(json.dumps(current_message), websocket)
    except Exception as e:
        logger.error(f"Error enviando datos actuales: {e}")

    try:
        while True:
            # Mantener la conexión viva
            data = await websocket.receive_text()
            # Procesar comandos del cliente si es necesario
            try:
                command = json.loads(data)
                if command.get("type") == "ping":
                    response = {
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    }
                    await websocket_manager.send_personal_message(json.dumps(response), websocket)
            except json.JSONDecodeError:
                pass  # Ignorar mensajes no JSON

    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
        logger.info("Cliente WebSocket desconectado")
    except Exception as e:
        logger.error(f"Error en WebSocket: {e}")
        websocket_manager.disconnect(websocket)


# Función principal simplificada
def main():
    """Función principal que ejecuta el servidor"""
    try:
        logger.info("Iniciando sistema de producción...")

        # Configurar manejo de señales
        def signal_handler(signum, frame):
            logger.info("Cerrando sistema...")
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Ejecutar FastAPI con uvicorn (incluye el servidor Modbus en lifespan)
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info",
            access_log=True
        )

    except KeyboardInterrupt:
        logger.info("Sistema interrumpido por usuario")
    except Exception as e:
        logger.error(f"Error crítico: {e}")


if __name__ == "__main__":
    main()