"""
Domain models for the production system.
These are pure Python classes representing business entities.
"""
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from typing import Dict, Optional


class ProductionStatus(Enum):
    """Production line status enumeration."""
    STOPPED = 0
    RUNNING = 1
    ERROR = 2
    MAINTENANCE = 3


class QualityStatus(Enum):
    """Product quality status enumeration."""
    NOK = 0
    OK = 1
    PENDING = 2


@dataclass
class ProductionData:
    """Production data entity representing a single production record."""
    
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
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['quality_status'] = self.quality_status.value
        data['line_status'] = self.line_status.value
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> 'ProductionData':
        """Create instance from dictionary."""
        # Convert string timestamp back to datetime
        if isinstance(data['timestamp'], str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        
        # Convert enum values back to enums
        if isinstance(data['quality_status'], int):
            data['quality_status'] = QualityStatus(data['quality_status'])
        
        if isinstance(data['line_status'], int):
            data['line_status'] = ProductionStatus(data['line_status'])
        
        return cls(**data)


@dataclass
class SystemEvent:
    """System event entity for logging important occurrences."""
    
    timestamp: datetime
    event_type: str
    severity: str
    message: str
    source: str
    resolved: bool = False
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class ProductionStats:
    """Production statistics aggregate."""
    
    total_products: int
    quality_ok_count: int
    quality_nok_count: int
    quality_pending_count: int
    quality_rate_percentage: float
    average_cycle_time_ms: float
    last_update: datetime
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['last_update'] = self.last_update.isoformat()
        return data


@dataclass
class ModbusRegisterData:
    """Modbus register data entity."""
    
    address: int
    values: list
    timestamp: datetime
    source: str = "PLC"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data 