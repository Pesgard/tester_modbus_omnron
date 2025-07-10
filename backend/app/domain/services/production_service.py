"""
Production service containing business logic for production data processing.
"""
from datetime import datetime, timedelta
from typing import List, Optional, Protocol
from abc import ABC, abstractmethod

from ..models import ProductionData, ProductionStats, QualityStatus, ProductionStatus


class ProductionRepository(Protocol):
    """Repository interface for production data persistence."""
    
    def save(self, data: ProductionData) -> bool:
        """Save production data."""
        ...
    
    def find_by_date_range(self, start_date: Optional[datetime], 
                          end_date: Optional[datetime], 
                          limit: int = 1000) -> List[ProductionData]:
        """Find production data by date range."""
        ...
    
    def find_latest(self, limit: int = 1) -> List[ProductionData]:
        """Find latest production records."""
        ...


class BatchIdGenerator(Protocol):
    """Interface for generating batch IDs."""
    
    def generate(self) -> str:
        """Generate a new batch ID."""
        ...


class ProductionService:
    """Service for production data business logic."""
    
    def __init__(self, repository: ProductionRepository, batch_generator: BatchIdGenerator):
        self.repository = repository
        self.batch_generator = batch_generator
        self.current_batch_id = self.batch_generator.generate()
    
    def process_plc_data(self, address: int, values: List[int]) -> Optional[ProductionData]:
        """
        Process raw PLC data and convert to production data.
        
        Args:
            address: Modbus register address
            values: List of register values
            
        Returns:
            ProductionData if successfully processed, None otherwise
        """
        try:
            if address == 0 and len(values) >= 10:
                return self._process_legacy_format(values)
            elif address == 1 and len(values) >= 10:
                return self._process_new_format(values)
            else:
                # Log or handle other addresses
                return None
        except Exception as e:
            # Log error
            return None
    
    def _process_legacy_format(self, values: List[int]) -> ProductionData:
        """Process legacy format data (address 0)."""
        return ProductionData(
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
            batch_id=self.current_batch_id
        )
    
    def _process_new_format(self, values: List[int]) -> ProductionData:
        """Process new format data (address 1)."""
        return ProductionData(
            timestamp=datetime.now(),
            product_id=values[0],
            quality_status=QualityStatus(values[1]),
            production_count=values[2],
            line_status=ProductionStatus(values[5]),
            error_code=values[6],
            cycle_time_ms=values[7],
            temperature=25.0,  # Default, should be from process registers
            pressure=4.0,      # Default, should be from process registers
            operator_id=values[8],
            batch_id=self.current_batch_id
        )
    
    def save_production_data(self, data: ProductionData) -> bool:
        """Save production data using repository."""
        return self.repository.save(data)
    
    def get_current_production_data(self) -> Optional[ProductionData]:
        """Get the most recent production data."""
        latest = self.repository.find_latest(limit=1)
        return latest[0] if latest else None
    
    def get_production_history(self, start_date: Optional[datetime] = None,
                              end_date: Optional[datetime] = None,
                              limit: int = 100) -> List[ProductionData]:
        """Get production history with optional date filtering."""
        return self.repository.find_by_date_range(start_date, end_date, limit)
    
    def calculate_statistics(self, start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None) -> ProductionStats:
        """Calculate production statistics for a given period."""
        if start_date is None:
            # Default to today
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        data = self.repository.find_by_date_range(start_date, end_date, limit=10000)
        
        if not data:
            return ProductionStats(
                total_products=0,
                quality_ok_count=0,
                quality_nok_count=0,
                quality_pending_count=0,
                quality_rate_percentage=0.0,
                average_cycle_time_ms=0.0,
                last_update=datetime.now()
            )
        
        total_products = len(data)
        quality_ok_count = len([d for d in data if d.quality_status == QualityStatus.OK])
        quality_nok_count = len([d for d in data if d.quality_status == QualityStatus.NOK])
        quality_pending_count = len([d for d in data if d.quality_status == QualityStatus.PENDING])
        
        quality_rate = (quality_ok_count / total_products * 100) if total_products > 0 else 0
        
        total_cycle_time = sum(d.cycle_time_ms for d in data)
        average_cycle_time = total_cycle_time / total_products if total_products > 0 else 0
        
        return ProductionStats(
            total_products=total_products,
            quality_ok_count=quality_ok_count,
            quality_nok_count=quality_nok_count,
            quality_pending_count=quality_pending_count,
            quality_rate_percentage=round(quality_rate, 2),
            average_cycle_time_ms=round(average_cycle_time, 2),
            last_update=datetime.now()
        )
    
    def start_new_batch(self) -> str:
        """Start a new production batch."""
        self.current_batch_id = self.batch_generator.generate()
        return self.current_batch_id
    
    def get_current_batch_id(self) -> str:
        """Get the current batch ID."""
        return self.current_batch_id
    
    def is_production_line_healthy(self) -> bool:
        """Check if production line is in a healthy state."""
        current_data = self.get_current_production_data()
        if not current_data:
            return False
        
        # Check if line is running and no critical errors
        is_running = current_data.line_status == ProductionStatus.RUNNING
        no_critical_error = current_data.error_code == 0
        
        # Check if data is recent (within last 5 minutes)
        time_threshold = datetime.now() - timedelta(minutes=5)
        is_recent = current_data.timestamp > time_threshold
        
        return is_running and no_critical_error and is_recent 