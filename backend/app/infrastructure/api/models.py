"""
Pydantic models for API request/response schemas.
These models provide automatic validation and documentation for the FastAPI endpoints.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator
from enum import Enum

from ...infrastructure.database.models import UserRole


class QualityStatusEnum(str, Enum):
    """Quality status enumeration for API responses."""
    NOK = "NOK"
    OK = "OK" 
    PENDING = "PENDING"


class ProductionStatusEnum(str, Enum):
    """Production line status enumeration for API responses."""
    STOPPED = "STOPPED"
    RUNNING = "RUNNING"
    ERROR = "ERROR"
    MAINTENANCE = "MAINTENANCE"


# Authentication Models
class LoginRequest(BaseModel):
    """
    User login credentials.
    
    Use these credentials to authenticate and receive a JWT token.
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "admin",
                "password": "admin123"
            }
        }
    )
    
    username: str = Field(description="Username for authentication", min_length=3, max_length=50)
    password: str = Field(description="User password", min_length=6, max_length=100)


class UserInfo(BaseModel):
    """Basic user information included in token response."""
    
    id: int = Field(description="Unique user identifier")
    username: str = Field(description="Username")
    email: str = Field(description="User email address")
    full_name: Optional[str] = Field(default=None, description="Full name of the user")
    role: str = Field(description="User role in the system")
    is_active: bool = Field(description="Whether the user account is active")


class TokenResponse(BaseModel):
    """
    JWT authentication token response.
    
    Contains the access token and user information for authenticated sessions.
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800,
                "user": {
                    "id": 1,
                    "username": "admin",
                    "email": "admin@company.com",
                    "full_name": "Administrator",
                    "role": "admin",
                    "is_active": True
                }
            }
        }
    )
    
    access_token: str = Field(description="JWT access token for authentication")
    token_type: str = Field(default="bearer", description="Token type (always 'bearer')")
    expires_in: int = Field(description="Token expiration time in seconds")
    user: UserInfo = Field(description="Authenticated user information")


class UserResponse(BaseModel):
    """
    Complete user information response.
    
    Used for user profile and user management endpoints.
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "username": "admin",
                "email": "admin@company.com",
                "full_name": "Administrator",
                "role": "admin",
                "is_active": True,
                "last_login": "2024-01-01T12:00:00Z",
                "created_at": "2024-01-01T10:00:00Z"
            }
        }
    )
    
    id: int = Field(description="Unique user identifier")
    username: str = Field(description="Username")
    email: str = Field(description="User email address")
    full_name: Optional[str] = Field(default=None, description="Full name of the user")
    role: str = Field(description="User role in the system")
    is_active: bool = Field(description="Whether the user account is active")
    last_login: Optional[datetime] = Field(default=None, description="Last login timestamp")
    created_at: datetime = Field(description="Account creation timestamp")


class CreateUserRequest(BaseModel):
    """
    Request to create a new user account.
    
    Admin-only operation for user management.
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "operator1",
                "email": "operator1@company.com",
                "password": "secure_password123",
                "full_name": "Production Operator",
                "role": "operator"
            }
        }
    )
    
    username: str = Field(description="Unique username for the new account", min_length=3, max_length=50)
    email: str = Field(description="Email address for the new user")
    password: str = Field(description="Password for the new account", min_length=8, max_length=100)
    full_name: Optional[str] = Field(default=None, description="Full name of the new user", max_length=200)
    role: UserRole = Field(default=UserRole.VIEWER, description="Role to assign to the new user")
    
    @field_validator('email')
    @classmethod
    def email_must_be_valid(cls, v: str) -> str:
        """Validate email format."""
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v


# Production Data Models
class ProductionDataResponse(BaseModel):
    """
    Production data from manufacturing equipment.
    
    Contains all relevant information about a production cycle including quality metrics.
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "timestamp": "2024-01-01T12:00:00Z",
                "product_id": 12345,
                "quality_status": "OK",
                "production_count": 100,
                "line_status": "RUNNING",
                "error_code": 0,
                "cycle_time_ms": 2500,
                "temperature": 25.5,
                "pressure": 4.2,
                "operator_id": 1,
                "batch_id": "BATCH_20240101_001"
            }
        }
    )
    
    timestamp: datetime = Field(description="Timestamp when the data was recorded")
    product_id: int = Field(description="Unique identifier for the manufactured product", ge=0)
    quality_status: QualityStatusEnum = Field(description="Quality assessment result")
    production_count: int = Field(description="Total number of products produced in this session", ge=0)
    line_status: ProductionStatusEnum = Field(description="Current status of the production line")
    error_code: int = Field(description="Error code (0 means no error)", ge=0)
    cycle_time_ms: int = Field(description="Production cycle time in milliseconds", gt=0)
    temperature: float = Field(description="Operating temperature in Celsius")
    pressure: float = Field(description="Operating pressure in bar", ge=0)
    operator_id: int = Field(description="ID of the operator managing this production", ge=1)
    batch_id: str = Field(description="Unique identifier for the production batch")


class ProductionStatsResponse(BaseModel):
    """
    Production statistics and quality metrics.
    
    Aggregated data providing insights into production performance.
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_products": 1000,
                "quality_ok_count": 950,
                "quality_nok_count": 30,
                "quality_pending_count": 20,
                "quality_rate_percentage": 95.0,
                "average_cycle_time_ms": 2450.5,
                "last_update": "2024-01-01T12:00:00Z"
            }
        }
    )
    
    total_products: int = Field(description="Total number of products produced", ge=0)
    quality_ok_count: int = Field(description="Number of products with OK quality status", ge=0)
    quality_nok_count: int = Field(description="Number of products with NOK quality status", ge=0)
    quality_pending_count: int = Field(description="Number of products with pending quality assessment", ge=0)
    quality_rate_percentage: float = Field(description="Percentage of products with OK quality", ge=0, le=100)
    average_cycle_time_ms: float = Field(description="Average production cycle time in milliseconds", gt=0)
    last_update: datetime = Field(description="Timestamp of the last statistics update")


# System Models
class ServiceStatus(BaseModel):
    """Status information for a system service."""
    
    modbus_server: str = Field(description="Modbus server status")
    database: str = Field(description="Database connection status")
    api: str = Field(description="API server status")
    production_line: str = Field(description="Production line status")


class HealthCheckResponse(BaseModel):
    """
    System health check response.
    
    Provides comprehensive status information about all system components.
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "healthy",
                "timestamp": "2024-01-01T12:00:00Z",
                "services": {
                    "modbus_server": "running",
                    "database": "connected",
                    "api": "running",
                    "production_line": "healthy"
                },
                "current_batch": "BATCH_20240101_001"
            }
        }
    )
    
    status: str = Field(description="Overall system health status")
    timestamp: datetime = Field(description="Health check timestamp")
    services: ServiceStatus = Field(description="Individual service status information")
    current_batch: Optional[str] = Field(default=None, description="Currently active production batch ID")


# Response Models
class ApiResponse(BaseModel):
    """Standard API response wrapper."""
    
    status: str = Field(description="Response status")
    message: Optional[str] = Field(default=None, description="Response message")
    timestamp: Optional[datetime] = Field(default=None, description="Response timestamp")


class ProductionHistoryResponse(ApiResponse):
    """Response for production history endpoints."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "success",
                "data": [
                    {
                        "timestamp": "2024-01-01T12:00:00Z",
                        "product_id": 12345,
                        "quality_status": "OK",
                        "production_count": 100,
                        "line_status": "RUNNING",
                        "error_code": 0,
                        "cycle_time_ms": 2500,
                        "temperature": 25.5,
                        "pressure": 4.2,
                        "operator_id": 1,
                        "batch_id": "BATCH_20240101_001"
                    }
                ],
                "count": 1
            }
        }
    )
    
    data: List[ProductionDataResponse] = Field(description="List of production records")
    count: int = Field(description="Number of records returned")


class NewBatchResponse(ApiResponse):
    """Response for new batch creation."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "success",
                "message": "New batch started",
                "batch_id": "BATCH_20240101_002",
                "timestamp": "2024-01-01T12:30:00Z"
            }
        }
    )
    
    batch_id: str = Field(description="ID of the newly created batch")


class DebugDataResponse(ApiResponse):
    """Response for debug/diagnostic endpoints."""
    
    recent_data: List[ProductionDataResponse] = Field(description="Recent production records")
    system_info: Dict[str, Any] = Field(description="System diagnostic information") 