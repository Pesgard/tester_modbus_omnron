"""
SQLAlchemy models for the production system database.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Boolean, Text, 
    ForeignKey, Table, Enum as SQLEnum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from ...domain.models import ProductionStatus, QualityStatus

Base = declarative_base()


class UserRole(enum.Enum):
    """User roles enumeration."""
    ADMIN = "admin"
    OPERATOR = "operator"
    SUPERVISOR = "supervisor"
    VIEWER = "viewer"


# Association table for user permissions
user_permissions = Table(
    'user_permissions',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True)
)


class User(Base):
    """User model for authentication and authorization."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.VIEWER)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    permissions = relationship("Permission", secondary=user_permissions, back_populates="users")
    production_records = relationship("ProductionRecord", back_populates="operator")
    
    def __repr__(self):
        return f"<User(username='{self.username}', role='{self.role.value}')>"


class Permission(Base):
    """Permission model for fine-grained access control."""
    
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(200), nullable=True)
    resource = Column(String(50), nullable=False)  # e.g., 'production', 'system', 'users'
    action = Column(String(50), nullable=False)    # e.g., 'read', 'write', 'delete'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    users = relationship("User", secondary=user_permissions, back_populates="permissions")
    
    def __repr__(self):
        return f"<Permission(name='{self.name}', resource='{self.resource}', action='{self.action}')>"


class ProductionRecord(Base):
    """Production data record model."""
    
    __tablename__ = "production_records"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    product_id = Column(Integer, nullable=False)
    quality_status = Column(SQLEnum(QualityStatus), nullable=False)
    production_count = Column(Integer, nullable=False)
    line_status = Column(SQLEnum(ProductionStatus), nullable=False)
    error_code = Column(Integer, nullable=False, default=0)
    cycle_time_ms = Column(Integer, nullable=False)
    temperature = Column(Float, nullable=False)
    pressure = Column(Float, nullable=False)
    operator_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    batch_id = Column(String(50), nullable=False, index=True)
    shift_id = Column(String(20), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    operator = relationship("User", back_populates="production_records")
    quality_data = relationship("QualityRecord", back_populates="production_record")
    process_data = relationship("ProcessRecord", back_populates="production_record")
    
    def __repr__(self):
        return f"<ProductionRecord(id={self.id}, product_id={self.product_id}, batch_id='{self.batch_id}')>"


class QualityRecord(Base):
    """Quality control data record model."""
    
    __tablename__ = "quality_records"
    
    id = Column(Integer, primary_key=True, index=True)
    production_record_id = Column(Integer, ForeignKey('production_records.id'), nullable=False)
    dimension_1 = Column(Float, nullable=True)  # mm
    dimension_2 = Column(Float, nullable=True)  # mm
    surface_roughness = Column(Float, nullable=True)  # μm
    hardness = Column(Float, nullable=True)  # HRC
    visual_inspection = Column(Boolean, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    production_record = relationship("ProductionRecord", back_populates="quality_data")
    
    def __repr__(self):
        return f"<QualityRecord(id={self.id}, production_record_id={self.production_record_id})>"


class ProcessRecord(Base):
    """Process parameters record model."""
    
    __tablename__ = "process_records"
    
    id = Column(Integer, primary_key=True, index=True)
    production_record_id = Column(Integer, ForeignKey('production_records.id'), nullable=False)
    temperature_line1 = Column(Float, nullable=True)  # °C
    temperature_line2 = Column(Float, nullable=True)  # °C
    hydraulic_pressure = Column(Float, nullable=True)  # bar
    air_pressure = Column(Float, nullable=True)  # bar
    line_speed = Column(Integer, nullable=True)  # units/min
    vibration = Column(Float, nullable=True)  # Hz
    power_consumption = Column(Float, nullable=True)  # A
    lubricant_level = Column(Integer, nullable=True)  # %
    sensor_status = Column(Integer, nullable=True)  # bitmask
    active_alarms = Column(Integer, nullable=True)  # bitmask
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    production_record = relationship("ProductionRecord", back_populates="process_data")
    
    def __repr__(self):
        return f"<ProcessRecord(id={self.id}, production_record_id={self.production_record_id})>"


class SystemEvent(Base):
    """System events and alerts model."""
    
    __tablename__ = "system_events"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    event_type = Column(String(50), nullable=False)  # 'error', 'warning', 'info', 'security'
    severity = Column(String(20), nullable=False)    # 'low', 'medium', 'high', 'critical'
    message = Column(Text, nullable=False)
    source = Column(String(50), nullable=False)      # 'modbus', 'api', 'system', 'user'
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    resolved = Column(Boolean, default=False)
    resolved_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    event_metadata = Column(Text, nullable=True)  # JSON string for additional data
    
    def __repr__(self):
        return f"<SystemEvent(id={self.id}, event_type='{self.event_type}', severity='{self.severity}')>"


class SystemConfig(Base):
    """System configuration model."""
    
    __tablename__ = "system_config"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False, default='general')
    is_sensitive = Column(Boolean, default=False)  # For passwords, API keys, etc.
    updated_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<SystemConfig(key='{self.key}', category='{self.category}')>"


class AuditLog(Base):
    """Audit log for tracking user actions."""
    
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    action = Column(String(100), nullable=False)
    resource = Column(String(100), nullable=False)
    resource_id = Column(String(50), nullable=True)
    ip_address = Column(String(45), nullable=True)  # Support IPv6
    user_agent = Column(String(500), nullable=True)
    details = Column(Text, nullable=True)  # JSON string for additional data
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, user_id={self.user_id}, action='{self.action}')>" 