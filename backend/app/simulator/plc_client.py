"""
PLC simulator client for testing the production system.
This simulates a PLC sending production data via Modbus TCP.
"""
import asyncio
import random
import time
from typing import List

from pymodbus.client import ModbusTcpClient
from ..infrastructure.logging.config import get_logger

logger = get_logger(__name__)


class PLCSimulator:
    """Simulates a PLC sending production data."""
    
    def __init__(self, host: str = "localhost", port: int = 502):
        self.host = host
        self.port = port
        self.client = None
        self.running = False
        self.product_counter = 0
        self.ok_count = 0
        self.nok_count = 0
        
    def connect(self) -> bool:
        """Connect to Modbus server."""
        try:
            self.client = ModbusTcpClient(self.host, port=self.port)
            result = self.client.connect()
            if result:
                logger.info(f"PLC Simulator connected to {self.host}:{self.port}")
            else:
                logger.error("Failed to connect to Modbus server")
            return result
        except Exception as e:
            logger.error(f"Error connecting to Modbus server: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from Modbus server."""
        if self.client:
            self.client.close()
            logger.info("PLC Simulator disconnected")
    
    def generate_production_data(self) -> List[int]:
        """Generate simulated production data."""
        self.product_counter += 1
        
        # Simulate quality status (80% OK, 20% NOK)
        quality_status = 1 if random.random() < 0.8 else 0
        if quality_status == 1:
            self.ok_count += 1
        else:
            self.nok_count += 1
        
        # Simulate line status (90% running, 10% other states)
        line_status = random.choices([1, 0, 2, 3], weights=[90, 5, 3, 2])[0]
        
        # Simulate error code (95% no error)
        error_code = 0 if random.random() < 0.95 else random.randint(1, 10)
        
        # Main production data (address 1)
        production_data = [
            self.product_counter,          # product_id
            quality_status,                # quality_status (0=NOK, 1=OK, 2=PENDING)
            self.product_counter,          # production_count
            self.ok_count,                 # ok_count
            self.nok_count,                # nok_count
            line_status,                   # line_status (0=STOPPED, 1=RUNNING, 2=ERROR, 3=MAINTENANCE)
            error_code,                    # error_code
            random.randint(1500, 3000),    # cycle_time_ms
            random.randint(1, 5),          # operator_id
            random.randint(1, 3)           # station_id
        ]
        
        return production_data
    
    def generate_process_data(self) -> List[int]:
        """Generate simulated process data."""
        return [
            random.randint(200, 300),      # temperature (°C * 10)
            random.randint(50, 80),        # humidity (% * 10)
            random.randint(35, 50),        # hydraulic_pressure (bar * 10)
            random.randint(40, 60),        # air_pressure (bar * 10)
            random.randint(0, 1),          # alarm_status
            random.randint(450, 550),      # vibration (Hz * 10)
            random.randint(1800, 2200),    # motor_speed (rpm)
            random.randint(80, 120)        # power_consumption (A * 10)
        ]
    
    def generate_quality_data(self) -> List[int]:
        """Generate simulated quality data."""
        return [
            random.randint(990, 1010),     # dimension_1 (mm * 100)
            random.randint(495, 505),      # dimension_2 (mm * 100)
            random.randint(98, 102),       # surface_roughness (μm * 100)
            random.randint(45, 55),        # hardness (HRC * 10)
            random.randint(0, 1)           # visual_inspection (0=NOK, 1=OK)
        ]
    
    def send_data(self, address: int, values: List[int]) -> bool:
        """Send data to Modbus server."""
        try:
            if not self.client or not self.client.connected:
                return False
            
            # Write holding registers
            result = self.client.write_registers(address, values)
            
            if result.isError():
                logger.error(f"Error writing to address {address}: {result}")
                return False
            else:
                logger.info(f"📤 Sent data to address {address}: {values[:5]}...")
                return True
                
        except Exception as e:
            logger.error(f"Error sending data: {e}")
            return False
    
    async def run_simulation(self, interval: float = 2.0):
        """Run continuous simulation."""
        if not self.connect():
            return
        
        self.running = True
        logger.info("🚀 Starting PLC simulation...")
        
        try:
            while self.running:
                # Send main production data (address 1)
                production_data = self.generate_production_data()
                self.send_data(1, production_data)
                
                # Send process data (address 41) every 3rd cycle
                if self.product_counter % 3 == 0:
                    process_data = self.generate_process_data()
                    self.send_data(41, process_data)
                
                # Send quality data (address 21) every 2nd cycle
                if self.product_counter % 2 == 0:
                    quality_data = self.generate_quality_data()
                    self.send_data(21, quality_data)
                
                await asyncio.sleep(interval)
                
        except KeyboardInterrupt:
            logger.info("Simulation interrupted by user")
        except Exception as e:
            logger.error(f"Error in simulation: {e}")
        finally:
            self.running = False
            self.disconnect()
    
    def stop(self):
        """Stop simulation."""
        self.running = False


async def main():
    """Main function to run PLC simulator."""
    simulator = PLCSimulator()
    
    try:
        await simulator.run_simulation(interval=2.0)
    except KeyboardInterrupt:
        logger.info("Simulator stopped")
    finally:
        simulator.stop()


if __name__ == "__main__":
    asyncio.run(main())