"""
Modbus server implementation for receiving PLC data.
"""
import asyncio
import logging
from typing import List, Callable, Optional

from pymodbus.server import StartAsyncTcpServer
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.device import ModbusDeviceIdentification

from ...core.config import settings

logger = logging.getLogger(__name__)


class ProductionDataBlock(ModbusSequentialDataBlock):
    """Custom Modbus data block that captures PLC writes."""
    
    def __init__(self, address: int, values: List[int], data_handler: Callable[[int, List[int]], None]):
        super().__init__(address, values)
        self.data_handler = data_handler
        self.last_update = 0
    
    def setValues(self, address: int, values: List[int]) -> None:
        """Capture when PLC writes data."""
        try:
            old_values = self.getValues(address, len(values))
            super().setValues(address, values)
            
            # Only process if there are real changes
            if old_values != values:
                self.data_handler(address, values)
                
                # Detailed logging
                if address in [0, 1]:
                    logger.info(f"📡 PLC wrote MAIN DATA at address {address}: {values[:10]}")
                elif address in [20, 21]:
                    logger.info(f"📊 PLC wrote QUALITY DATA at address {address}: {values[:5]}")
                elif address in [40, 41]:
                    logger.info(f"🌡️ PLC wrote PROCESS DATA at address {address}: Temp={values[0]/10}°C, Press={values[2]/10}bar")
                else:
                    logger.info(f"📝 PLC wrote at address {address}: {values}")
                    
        except Exception as e:
            logger.error(f"Error processing PLC data: {e}")


class ModbusServer:
    """Modbus TCP server for receiving production data from PLC."""
    
    def __init__(self, data_handler: Callable[[int, List[int]], None], 
                 host: Optional[str] = None, port: Optional[int] = None):
        self.host = host or settings.modbus_host
        self.port = port or settings.modbus_port
        self.data_handler = data_handler
        self.server_task: Optional[asyncio.Task] = None
        self.context = None
    
    async def start(self):
        """Start the Modbus server."""
        try:
            # Create data blocks with custom handler
            # Expand block to cover addresses 0-199 (includes 1, 21, 41 used by client)
            store = ModbusSlaveContext(
                di=ModbusSequentialDataBlock(0, [0] * 200),  # Discrete Inputs
                co=ModbusSequentialDataBlock(0, [0] * 200),  # Coils
                hr=ProductionDataBlock(0, [0] * 200, self.data_handler),  # Holding Registers
                ir=ModbusSequentialDataBlock(0, [0] * 200)   # Input Registers
            )
            
            self.context = ModbusServerContext(slaves=store, single=True)
            
            # Device identity
            identity = ModbusDeviceIdentification()
            identity.VendorName = 'Production System'
            identity.ProductCode = 'PS'
            identity.VendorUrl = 'http://localhost'
            identity.ProductName = 'Production Modbus Server'
            identity.ModelName = 'Production Server v2.0'
            identity.MajorMinorRevision = '2.0'
            
            logger.info(f"Starting Modbus server on {self.host}:{self.port}")
            logger.info("Server configured to receive data at addresses 0-199")
            logger.info("Expected PLC addresses: 1 (main), 21 (quality), 41 (process)")
            
            self.server_task = asyncio.create_task(
                StartAsyncTcpServer(
                    context=self.context,
                    identity=identity,
                    address=(self.host, self.port)
                )
            )
            
            await self.server_task
            
        except Exception as e:
            logger.error(f"Error starting Modbus server: {e}")
            raise
    
    def stop(self):
        """Stop the Modbus server."""
        if self.server_task:
            self.server_task.cancel()
            logger.info("Modbus server stopped")
    
    def get_register_values(self, address: int, count: int) -> List[int]:
        """Get current register values."""
        if self.context:
            try:
                slave = self.context[0]  # Single slave context
                return slave.getValues(3, address, count)  # 3 = holding registers
            except (KeyError, AttributeError):
                pass
        return []
    
    def set_register_values(self, address: int, values: List[int]):
        """Set register values (for testing/simulation)."""
        if self.context:
            try:
                slave = self.context[0]
                slave.setValues(3, address, values)  # 3 = holding registers
            except (KeyError, AttributeError):
                pass 