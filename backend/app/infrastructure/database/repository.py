"""
Database repository implementation using SQLAlchemy with PostgreSQL.
Provides data access layer for the production system.
"""
import logging
import json
import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any, Tuple, AsyncGenerator
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload
from sqlalchemy import select, func, and_, or_, desc, asc
from sqlalchemy.exc import SQLAlchemyError
from passlib.context import CryptContext

from ...domain.models import ProductionData, ProductionStats, ProductionStatus, QualityStatus
from ...core.config import settings
from .models import (
    Base, User, Permission, ProductionRecord, QualityRecord, 
    ProcessRecord, SystemEvent, SystemConfig, AuditLog, UserRole
)

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Async database manager using SQLAlchemy."""
    
    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or settings.database_url
        self.engine = create_async_engine(
            self.database_url,
            echo=settings.database_echo,
            pool_size=settings.database_pool_size,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=3600
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def create_tables(self):
        """Create all database tables."""
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
        except SQLAlchemyError as e:
            logger.error(f"Error creating database tables: {e}")
            raise
    
    async def drop_tables(self):
        """Drop all database tables."""
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
            logger.info("Database tables dropped successfully")
        except SQLAlchemyError as e:
            logger.error(f"Error dropping database tables: {e}")
            raise
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Context manager for database sessions."""
        async with self.session_factory() as session:
            try:
                yield session
            except SQLAlchemyError as e:
                await session.rollback()
                logger.error(f"Database session error: {e}")
                raise
            finally:
                await session.close()
    
    async def close(self):
        """Close database connections."""
        await self.engine.dispose()


class UserRepository:
    """Repository for user management."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    async def create_user(self, username: str, email: str, password: str, 
                         full_name: Optional[str] = None, 
                         role: UserRole = UserRole.VIEWER) -> Optional[User]:
        """Create a new user."""
        try:
            async with self.db_manager.get_session() as session:
                # Check if user already exists
                existing_user = await session.execute(
                    select(User).where(
                        or_(User.username == username, User.email == email)
                    )
                )
                if existing_user.scalar_one_or_none():
                    return None
                
                # Create new user
                hashed_password = self.pwd_context.hash(password)
                user = User(
                    username=username,
                    email=email,
                    hashed_password=hashed_password,
                    full_name=full_name,
                    role=role
                )
                session.add(user)
                await session.commit()
                await session.refresh(user)
                return user
        except SQLAlchemyError as e:
            logger.error(f"Error creating user: {e}")
            return None
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        try:
            async with self.db_manager.get_session() as session:
                result = await session.execute(
                    select(User).where(User.username == username)
                    .options(selectinload(User.permissions))
                )
                return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Error getting user by username: {e}")
            return None
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        try:
            async with self.db_manager.get_session() as session:
                result = await session.execute(
                    select(User).where(User.id == user_id)
                    .options(selectinload(User.permissions))
                )
                return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Error getting user by ID: {e}")
            return None
    
    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password."""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    async def update_last_login(self, user_id: int) -> bool:
        """Update user's last login timestamp."""
        try:
            async with self.db_manager.get_session() as session:
                user = await session.get(User, user_id)
                if user:
                    user.last_login = datetime.now(timezone.utc)
                    await session.commit()
                    return True
                return False
        except SQLAlchemyError as e:
            logger.error(f"Error updating last login: {e}")
            return False
    
    async def list_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """List users with pagination."""
        try:
            async with self.db_manager.get_session() as session:
                result = await session.execute(
                    select(User).offset(skip).limit(limit)
                    .options(selectinload(User.permissions))
                )
                return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Error listing users: {e}")
            return []

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        try:
            async with self.db_manager.get_session() as session:
                result = await session.execute(select(User).where(User.email == email))
                return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Error getting user by email: {e}")
            return None


class ProductionRepository:
    """Repository for production data persistence."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    async def save(self, data: ProductionData, operator_id: Optional[int] = None) -> bool:
        """Save production data."""
        try:
            async with self.db_manager.get_session() as session:
                production_record = ProductionRecord(
                    timestamp=data.timestamp,
                    product_id=data.product_id,
                    quality_status=data.quality_status,
                    production_count=data.production_count,
                    line_status=data.line_status,
                    error_code=data.error_code,
                    cycle_time_ms=data.cycle_time_ms,
                    temperature=data.temperature,
                    pressure=data.pressure,
                    operator_id=operator_id,
                    batch_id=data.batch_id
                )
                session.add(production_record)
                await session.commit()
                return True
        except SQLAlchemyError as e:
            logger.error(f"Error saving production data: {e}")
            return False
    
    async def find_by_date_range(self, start_date: Optional[datetime] = None,
                                end_date: Optional[datetime] = None, 
                                limit: int = 1000) -> List[ProductionData]:
        """Find production data by date range."""
        try:
            async with self.db_manager.get_session() as session:
                query = select(ProductionRecord)
                
                conditions = []
                if start_date:
                    conditions.append(ProductionRecord.timestamp >= start_date)
                if end_date:
                    conditions.append(ProductionRecord.timestamp <= end_date)
                
                if conditions:
                    query = query.where(and_(*conditions))
                
                query = query.order_by(desc(ProductionRecord.timestamp)).limit(limit)
                
                result = await session.execute(query)
                records = result.scalars().all()
                
                return [self._record_to_production_data(record) for record in records]
        except SQLAlchemyError as e:
            logger.error(f"Error finding production data by date range: {e}")
            return []
    
    async def find_latest(self, limit: int = 1) -> List[ProductionData]:
        """Find latest production records."""
        try:
            async with self.db_manager.get_session() as session:
                result = await session.execute(
                    select(ProductionRecord)
                    .order_by(desc(ProductionRecord.timestamp))
                    .limit(limit)
                )
                records = result.scalars().all()
                
                return [self._record_to_production_data(record) for record in records]
        except SQLAlchemyError as e:
            logger.error(f"Error finding latest production data: {e}")
            return []
    
    async def get_production_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Get production statistics for the last N hours."""
        try:
            async with self.db_manager.get_session() as session:
                start_time = datetime.utcnow() - timedelta(hours=hours)
                
                # Total production count
                total_result = await session.execute(
                    select(func.sum(ProductionRecord.production_count))
                    .where(ProductionRecord.timestamp >= start_time)
                )
                total_production = total_result.scalar() or 0
                
                # Quality statistics
                quality_result = await session.execute(
                    select(
                        ProductionRecord.quality_status,
                        func.count(ProductionRecord.id)
                    )
                    .where(ProductionRecord.timestamp >= start_time)
                    .group_by(ProductionRecord.quality_status)
                )
                quality_stats = {status.name: count for status, count in quality_result.fetchall()}
                
                # Average cycle time
                cycle_time_result = await session.execute(
                    select(func.avg(ProductionRecord.cycle_time_ms))
                    .where(ProductionRecord.timestamp >= start_time)
                )
                avg_cycle_time = cycle_time_result.scalar() or 0
                
                return {
                    "total_production": total_production,
                    "quality_stats": quality_stats,
                    "average_cycle_time_ms": avg_cycle_time,
                    "period_hours": hours
                }
        except SQLAlchemyError as e:
            logger.error(f"Error getting production stats: {e}")
            return {}
    
    def _record_to_production_data(self, record: ProductionRecord) -> ProductionData:
        """Convert ProductionRecord to ProductionData."""
        return ProductionData(
            timestamp=record.timestamp.value,
            product_id=record.product_id.value,
            quality_status=QualityStatus(record.quality_status.value),
            production_count=record.production_count.value,
            line_status=ProductionStatus(record.line_status.value),
            error_code=record.error_code.value,
            cycle_time_ms=record.cycle_time_ms.value,
            temperature=record.temperature.value,
            pressure=record.pressure.value,
            operator_id=record.operator_id.value,
            batch_id=record.batch_id.value
        )


class SystemEventRepository:
    """Repository for system events."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    async def create_event(self, event_type: str, severity: str, message: str,
                          source: str, user_id: Optional[int] = None,
                          metadata: Optional[Dict] = None) -> bool:
        """Create a system event."""
        try:
            async with self.db_manager.get_session() as session:
                event = SystemEvent(
                    event_type=event_type,
                    severity=severity,
                    message=message,
                    source=source,
                    user_id=user_id,
                    metadata=json.dumps(metadata) if metadata else None
                )
                session.add(event)
                await session.commit()
                return True
        except SQLAlchemyError as e:
            logger.error(f"Error creating system event: {e}")
            return False
    
    async def get_recent_events(self, limit: int = 100) -> List[SystemEvent]:
        """Get recent system events."""
        try:
            async with self.db_manager.get_session() as session:
                result = await session.execute(
                    select(SystemEvent)
                    .order_by(desc(SystemEvent.timestamp))
                    .limit(limit)
                )
                return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Error getting recent events: {e}")
            return []


class AuditLogRepository:
    """Repository for audit logs."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    async def log_action(self, user_id: Optional[int], action: str, resource: str,
                        resource_id: Optional[str] = None, ip_address: Optional[str] = None,
                        user_agent: Optional[str] = None, details: Optional[Dict] = None) -> bool:
        """Log a user action."""
        try:
            async with self.db_manager.get_session() as session:
                audit_log = AuditLog(
                    user_id=user_id,
                    action=action,
                    resource=resource,
                    resource_id=resource_id,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    details=json.dumps(details) if details else None
                )
                session.add(audit_log)
                await session.commit()
                return True
        except SQLAlchemyError as e:
            logger.error(f"Error logging audit action: {e}")
            return False


class BatchIdGenerator:
    """Generator for batch IDs."""
    
    def __init__(self, prefix: Optional[str] = None):
        self.prefix = prefix or "BATCH"
    
    def generate(self) -> str:
        """Generate a new batch ID."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M")
        unique_id = str(uuid.uuid4())[:8].upper()
        return f"{self.prefix}_{timestamp}_{unique_id}"


# Initialize default repositories
async def init_default_data(db_manager: DatabaseManager):
    """Initialize default data in the database."""
    user_repo = UserRepository(db_manager)
    
    # Create default admin user if not exists
    admin_user = await user_repo.get_user_by_username("admin")
    if not admin_user:
        await user_repo.create_user(
            username="admin",
            email="admin@production.local",
            password="admin123",  # Should be changed in production
            full_name="System Administrator",
            role=UserRole.ADMIN
        )
        logger.info("Default admin user created")
    
    # Create default permissions
    async with db_manager.get_session() as session:
        # Check if permissions exist
        existing_perms = await session.execute(select(Permission))
        if not existing_perms.scalars().first():
            default_permissions = [
                Permission(name="production.read", description="Read production data", resource="production", action="read"),
                Permission(name="production.write", description="Write production data", resource="production", action="write"),
                Permission(name="system.read", description="Read system configuration", resource="system", action="read"),
                Permission(name="system.write", description="Write system configuration", resource="system", action="write"),
                Permission(name="users.read", description="Read user data", resource="users", action="read"),
                Permission(name="users.write", description="Write user data", resource="users", action="write"),
                Permission(name="users.delete", description="Delete users", resource="users", action="delete"),
            ]
            
            for perm in default_permissions:
                session.add(perm)
            
            await session.commit()
            logger.info("Default permissions created") 