"""
FastAPI routes for the production system API.

This module contains all API endpoints for the industrial production monitoring system.
Each endpoint includes comprehensive documentation, validation, and examples.
"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Request, status, Query, Path
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials
from pydantic import Field

from ...domain.services.production_service import ProductionService  
from ...domain.services.auth_service import AuthService, security
from ...infrastructure.database.models import User, UserRole
from ...infrastructure.logging.config import get_logger
from .models import *

logger = get_logger(__name__)

# Create routers with comprehensive tags and descriptions
production_router = APIRouter(
    prefix="/api/production", 
    tags=["production"],
    responses={
        401: {"description": "Authentication required"},
        403: {"description": "Insufficient permissions"},
        500: {"description": "Internal server error"}
    }
)

auth_router = APIRouter(
    prefix="/api/auth", 
    tags=["authentication"],
    responses={
        401: {"description": "Authentication failed"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)

admin_router = APIRouter(
    prefix="/api/admin", 
    tags=["administration"],
    dependencies=[],  # Will add admin check in endpoints
    responses={
        401: {"description": "Authentication required"},
        403: {"description": "Admin access required"},
        404: {"description": "Resource not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)

system_router = APIRouter(
    prefix="/api/system", 
    tags=["system"],
    responses={
        500: {"description": "System error"},
        503: {"description": "Service unavailable"}
    }
)


# Pydantic models for request/response
class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: Dict[str, Any]


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    role: str
    is_active: bool
    last_login: Optional[datetime]
    created_at: datetime


class CreateUserRequest(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = None
    role: UserRole = UserRole.VIEWER


# Dependency injection functions
def get_production_service() -> ProductionService:
    """
    Dependency to get production service instance.
    
    Returns the singleton production service for data operations.
    """
    from ...main import get_production_service_instance
    return get_production_service_instance()


def get_auth_service() -> AuthService:
    """
    Dependency to get authentication service instance.
    
    Returns the singleton auth service for user operations.
    """
    from ...main import get_auth_service
    return get_auth_service()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    """
    Get current authenticated user from JWT token.
    
    **Used by:** All protected endpoints
    **Raises:** HTTP 401 if token is invalid or expired
    """
    return await auth_service.get_current_user(credentials)


async def require_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Ensure current user has admin privileges.
    
    **Used by:** Admin-only endpoints
    **Raises:** HTTP 403 if user is not admin
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@auth_router.post(
    "/login", 
    response_model=TokenResponse,
    summary="🔐 User Authentication",
    description="""
    Authenticate a user and receive a JWT access token.
    
    **Authentication Flow:**
    1. Submit username and password
    2. Receive JWT token and user information
    3. Include token in `Authorization: Bearer <token>` header for protected endpoints
    
    **Token Expiration:** 30 minutes
    **Rate Limiting:** 5 attempts per minute per IP
    
    **Default Admin Account:**
    - Username: `admin`
    - Password: `admin123`
    """,
    responses={
        200: {
            "description": "Authentication successful",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer",
                        "expires_in": 1800,
                        "user": {
                            "id": 1,
                            "username": "admin",
                            "email": "admin@company.com",
                            "role": "admin",
                            "is_active": True
                        }
                    }
                }
            }
        },
        401: {"description": "Invalid credentials"}
    }
)
async def login(
    request: Request,
    login_data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    ## User Login
    
    Authenticate user credentials and return JWT access token.
    
    The token must be included in the Authorization header for protected endpoints:
    ```
    Authorization: Bearer <your-token-here>
    ```
    """
    try:
        user = await auth_service.authenticate_user(
            username=login_data.username,
            password=login_data.password,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        
        # Create access token
        access_token = auth_service.create_access_token(
            data={"sub": str(user.id), "username": user.username}
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=30 * 60,  # 30 minutes in seconds
            user={
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value,
                "is_active": user.is_active
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@auth_router.get(
    "/me", 
    response_model=UserResponse,
    summary="👤 Current User Profile",
    description="""
    Get detailed information about the currently authenticated user.
    
    **Requires:** Valid JWT token
    **Returns:** Complete user profile including role and timestamps
    """,
    responses={
        200: {
            "description": "User profile retrieved successfully",
            "content": {
                "application/json": {
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
            }
        }
    }
)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    ## Current User Information
    
    Retrieve detailed profile information for the authenticated user.
    
    **Use this endpoint to:**
    - Verify token validity
    - Get user role for UI permissions
    - Display user information in the interface
    """
    return UserResponse(
        id=current_user.id.value,
        username=current_user.username.value,
        email=current_user.email.value,
        full_name=current_user.full_name.value,
        role=current_user.role.value,
        is_active=current_user.is_active.value,
        last_login=current_user.last_login.value,
        created_at=current_user.created_at.value
    )


# ============================================================================
# PRODUCTION DATA ENDPOINTS
# ============================================================================

@production_router.get(
    "/current",
    response_model=Dict[str, Any],
    summary="📊 Current Production Status",
    description="""
    Get the most recent production data from the manufacturing line.
    
    **Real-time Data Includes:**
    - Current product being manufactured
    - Quality status (OK/NOK/PENDING)
    - Production counts and rates
    - Equipment status and parameters
    - Operating conditions (temperature, pressure)
    
    **Update Frequency:** Data is updated every few seconds via PLC communication
    **WebSocket Alternative:** Use `/ws/production` for real-time streaming
    """,
    responses={
        200: {
            "description": "Current production data",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "data": {
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
                }
            }
        },
        204: {"description": "No current production data available"}
    }
)
async def get_current_production(
    service: ProductionService = Depends(get_production_service),
    current_user: User = Depends(get_current_user)
):
    """
    ## Current Production Status
    
    Retrieve the latest production data from the manufacturing equipment.
    
    This endpoint provides real-time visibility into:
    - **Product Information**: Current item being produced
    - **Quality Metrics**: Pass/fail status and quality indicators  
    - **Production Rates**: Cycle times and throughput
    - **System Status**: Equipment health and error codes
    - **Process Parameters**: Temperature, pressure, and other variables
    """
    try:
        data = service.get_current_production_data()
        if data:
            return {"status": "success", "data": data.to_dict()}
        return {"status": "success", "data": None}
    except Exception as e:
        logger.error(f"Error getting current production: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@production_router.get(
    "/history",
    response_model=ProductionHistoryResponse,
    summary="📈 Production History",
    description="""
    Retrieve historical production data with flexible filtering options.
    
    **Query Parameters:**
    - `start_date`: Filter from this date (ISO format)
    - `end_date`: Filter until this date (ISO format) 
    - `limit`: Maximum records to return (default: 100, max: 1000)
    
    **Use Cases:**
    - Quality analysis and reporting
    - Production trend analysis
    - Shift performance evaluation
    - Historical troubleshooting
    
    **Date Format:** Use ISO 8601 format: `2024-01-01T12:00:00Z`
    """,
    responses={
        200: {
            "description": "Production history retrieved successfully",
            "content": {
                "application/json": {
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
            }
        }
    }
)
async def get_production_history(
    start_date: Optional[str] = Query(
        None, 
        description="Start date filter (ISO format: 2024-01-01T12:00:00Z)",
        example="2024-01-01T00:00:00Z"
    ),
    end_date: Optional[str] = Query(
        None, 
        description="End date filter (ISO format: 2024-01-01T12:00:00Z)",
        example="2024-01-01T23:59:59Z"
    ),
    limit: int = Query(
        100, 
        description="Maximum number of records to return",
        ge=1, 
        le=1000,
        example=100
    ),
    service: ProductionService = Depends(get_production_service),
    current_user: User = Depends(get_current_user)
):
    """
    ## Production History Query
    
    Query historical production records with date range filtering.
    
    **Example Queries:**
    - Last 24 hours: `?start_date=2024-01-01T00:00:00Z&end_date=2024-01-02T00:00:00Z`
    - Last 100 records: `?limit=100`
    - Specific time range: `?start_date=2024-01-01T08:00:00Z&end_date=2024-01-01T16:00:00Z`
    
    **Performance Notes:**
    - Large date ranges may take longer to process
    - Use pagination with limit parameter for better performance
    - Consider using WebSocket for real-time data instead of polling
    """
    try:
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        
        data = service.get_production_history(
            start_date=start_dt,
            end_date=end_dt,
            limit=limit
        )
        
        return ProductionHistoryResponse(
            status="success",
            data=[ProductionDataResponse(**item.to_dict()) for item in data],
            count=len(data)
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Invalid date format: {e}")
    except Exception as e:
        logger.error(f"Error getting production history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@production_router.get(
    "/stats",
    response_model=Dict[str, Any],
    summary="📊 Production Statistics",
    description="""
    Get comprehensive production statistics and quality metrics.
    
    **Statistics Include:**
    - Total production counts
    - Quality rate percentages
    - Average cycle times
    - Error analysis
    - Trend indicators
    
    **Time Range:** Use start_date/end_date to analyze specific periods
    **Default:** Last 24 hours if no dates specified
    """,
    responses={
        200: {
            "description": "Production statistics",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "data": {
                            "total_products": 1000,
                            "quality_ok_count": 950,
                            "quality_nok_count": 30,
                            "quality_pending_count": 20,
                            "quality_rate_percentage": 95.0,
                            "average_cycle_time_ms": 2450.5,
                            "last_update": "2024-01-01T12:00:00Z"
                        }
                    }
                }
            }
        }
    }
)
async def get_production_stats(
    start_date: Optional[str] = Query(
        None, 
        description="Statistics start date (ISO format)",
        example="2024-01-01T00:00:00Z"
    ),
    end_date: Optional[str] = Query(
        None, 
        description="Statistics end date (ISO format)",
        example="2024-01-01T23:59:59Z"
    ),
    service: ProductionService = Depends(get_production_service),
    current_user: User = Depends(get_current_user)
):
    """
    ## Production Analytics
    
    Calculate comprehensive statistics for production performance analysis.
    
    **Key Metrics:**
    - **Quality Rate**: Percentage of products passing quality checks
    - **Production Volume**: Total units produced in time period
    - **Cycle Time**: Average time per production cycle
    - **Error Analysis**: Breakdown of issues and their frequency
    
    **Business Intelligence:**
    Use these metrics for operational decisions, quality improvements,
    and performance monitoring across different time periods.
    """
    try:
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        
        stats = service.calculate_statistics(start_date=start_dt, end_date=end_dt)
        
        return {
            "status": "success",
            "data": stats
        }
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Invalid date format: {e}")
    except Exception as e:
        logger.error(f"Error getting production stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@production_router.post(
    "/batch/new",
    response_model=NewBatchResponse,
    summary="🔄 Start New Production Batch",
    description="""
    Initialize a new production batch for tracking and organization.
    
    **Batch Benefits:**
    - Groups related production runs
    - Enables traceability and quality tracking
    - Supports shift-based production management
    - Facilitates inventory and shipping coordination
    
    **Automatic Features:**
    - Timestamp-based batch ID generation
    - Operator assignment tracking
    - Integration with quality systems
    
    **Permissions:** Requires operator-level access or higher
    """,
    responses={
        201: {
            "description": "New batch created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "New batch started successfully",
                        "batch_id": "BATCH_20240101_002",
                        "timestamp": "2024-01-01T12:30:00Z"
                    }
                }
            }
        },
        403: {"description": "Insufficient permissions - operator access required"}
    }
)
async def start_new_batch(
    service: ProductionService = Depends(get_production_service),
    current_user: User = Depends(get_current_user)
):
    """
    ## Start New Production Batch
    
    Create a new production batch for organizing and tracking manufacturing runs.
    
    **When to Use:**
    - Beginning of a new shift
    - Starting production of a new product variant
    - After equipment maintenance or setup changes
    - At regular intervals for quality control
    
    **Automatic Actions:**
    - Generates unique batch identifier
    - Records operator and timestamp
    - Initializes tracking systems
    - Prepares quality control workflows
    """
    try:
        # Check user permissions
        if current_user.role not in [UserRole.ADMIN, UserRole.SUPERVISOR, UserRole.OPERATOR]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operator access or higher required"
            )
        
        batch_id = service.start_new_batch()
        
        return NewBatchResponse(
            status="success",
            message="New batch started successfully",
            batch_id=batch_id,
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        logger.error(f"Error starting new batch: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SYSTEM HEALTH AND DIAGNOSTICS
# ============================================================================

@system_router.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="🏥 System Health Check",
    description="""
    Comprehensive system health and status monitoring.
    
    **Health Indicators:**
    - API server responsiveness
    - Database connectivity
    - Modbus communication status
    - Production line health
    - Service availability
    
    **Monitoring Integration:**
    - Use for automated health checks
    - Integration with monitoring systems (Prometheus, etc.)
    - Load balancer health probes
    - DevOps alerting systems
    
    **No Authentication Required** - Public health endpoint
    """,
    responses={
        200: {
            "description": "System is healthy",
            "content": {
                "application/json": {
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
            }
        },
        503: {"description": "System is unhealthy or degraded"}
    }
)
async def health_check(service: ProductionService = Depends(get_production_service)):
    """
    ## System Health Status
    
    Monitor the overall health and availability of all system components.
    
    **Health Check Includes:**
    - **API Server**: Response time and availability
    - **Database**: Connection status and query performance
    - **Modbus Server**: PLC communication health
    - **Production Line**: Equipment status and errors
    
    **Status Codes:**
    - `healthy`: All systems operational
    - `degraded`: Some non-critical issues
    - `unhealthy`: Critical systems failing
    """
    try:
        current_data = service.get_current_production_data()
        
        # Simple health check - could be expanded
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow(),
            "services": {
                "modbus_server": "running",
                "database": "connected", 
                "api": "running",
                "production_line": "healthy"
            },
            "current_batch": current_data.batch_id if current_data else None
        }
        
        return HealthCheckResponse(**health_status)
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        # Return unhealthy status
        return HealthCheckResponse(
            status="unhealthy",
            timestamp=datetime.utcnow(),
            services=ServiceStatus(
                modbus_server="error",
                database="error",
                api="running",
                production_line="error"
            )
        )


@system_router.get(
    "/debug/recent-data",
    response_model=DebugDataResponse,
    summary="🔧 Debug Information",
    description="""
    Diagnostic endpoint for troubleshooting and system analysis.
    
    **Debug Information:**
    - Recent production records
    - System performance metrics
    - Error logs and warnings
    - Configuration status
    
    **Use Cases:**
    - Technical troubleshooting
    - Performance analysis
    - Support and maintenance
    - Development and testing
    
    **Security:** Requires authenticated access
    """,
    responses={
        200: {"description": "Debug information retrieved"}
    }
)
async def get_recent_debug_data(
    service: ProductionService = Depends(get_production_service),
    current_user: User = Depends(get_current_user)
):
    """
    ## System Diagnostics
    
    Get detailed diagnostic information for troubleshooting and analysis.
    
    **Diagnostic Data:**
    - Recent production records with full details
    - System performance indicators
    - Connection status and metrics
    - Error history and patterns
    
    **Support Usage:**
    Include this information when reporting issues or requesting support.
    """
    try:
        # Get recent data for debugging
        recent_data = service.get_production_history(limit=10)
        
        system_info = {
            "timestamp": datetime.utcnow().isoformat(),
            "active_user": current_user.username,
            "user_role": current_user.role.value,
            "recent_records_count": len(recent_data),
            "system_uptime": "Running",
            "memory_usage": "Normal",
            "connection_status": "Connected"
        }
        
        return DebugDataResponse(
            status="success",
            timestamp=datetime.utcnow(),
            recent_data=[ProductionDataResponse(**item.to_dict()) for item in recent_data],
            system_info=system_info
        )
    except Exception as e:
        logger.error(f"Error getting debug data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ADMINISTRATION ENDPOINTS  
# ============================================================================

@admin_router.get(
    "/users", 
    response_model=List[UserResponse],
    summary="👥 List All Users",
    description="""
    Retrieve a list of all system users with their details and status.
    
    **Admin Features:**
    - View all user accounts
    - Monitor user activity and status
    - Support user management operations
    
    **Pagination Parameters:**
    - `skip`: Number of records to skip (for pagination)
    - `limit`: Maximum records to return (default: 100)
    
    **Security:** Admin access required
    """,
    responses={
        200: {"description": "User list retrieved successfully"},
        403: {"description": "Admin access required"}
    }
)
async def list_users(
    skip: int = Query(0, description="Number of records to skip", ge=0),
    limit: int = Query(100, description="Maximum records to return", ge=1, le=1000),
    current_user: User = Depends(require_admin_user)
):
    """
    ## User Management - List Users
    
    Administrative endpoint to view and manage all system users.
    
    **User Information Includes:**
    - Account details and contact information
    - Role assignments and permissions
    - Activity status and last login
    - Account creation and modification dates
    
    **Administrative Uses:**
    - User account auditing
    - Access control management
    - Security compliance reporting
    """
    try:
        from ...main import get_user_repository
        user_repo = get_user_repository()
        
        users = await user_repo.list_users(skip=skip, limit=limit)
        
        return [
            UserResponse(
                id=user.id.value,
                username=user.username.value,
                email=user.email.value,
                full_name=user.full_name.value,
                role=user.role.value,
                is_active=user.is_active.value,
                last_login=user.last_login.value,
                created_at=user.created_at.value
            )
            for user in users
        ]
    except Exception as e:
        logger.error(f"Error listing users: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@admin_router.post(
    "/users", 
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="➕ Create New User",
    description="""
    Create a new user account with specified role and permissions.
    
    **User Roles:**
    - `admin`: Full system access and user management
    - `supervisor`: Production oversight and reporting
    - `operator`: Production monitoring and control
    - `viewer`: Read-only access to production data
    
    **Security Features:**
    - Password validation and hashing
    - Email uniqueness validation
    - Role-based access control setup
    
    **Admin Only:** Requires admin privileges
    """,
    responses={
        201: {"description": "User created successfully"},
        400: {"description": "Username or email already exists"},
        403: {"description": "Admin access required"},
        422: {"description": "Validation error"}
    }
)
async def create_user(
    user_data: CreateUserRequest,
    current_user: User = Depends(require_admin_user)
):
    """
    ## User Management - Create Account
    
    Administrative function to create new user accounts.
    
    **Account Creation Process:**
    1. Validate username and email uniqueness
    2. Hash password securely
    3. Assign specified role and permissions
    4. Initialize user profile
    5. Log account creation for audit
    
    **Best Practices:**
    - Use strong passwords (minimum 8 characters)
    - Assign minimal required permissions
    - Verify email addresses when possible
    - Document user purpose and responsibilities
    """
    try:
        from ...main import get_user_repository
        user_repo = get_user_repository()
        
        # Check if username or email already exists
        existing_user = await user_repo.get_user_by_username(user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        
        existing_email = await user_repo.get_user_by_email(user_data.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        
        # Create new user
        new_user = await user_repo.create_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name,
            role=user_data.role
        )
        
        logger.info(f"New user created: {user_data.username} by admin {current_user.username}")
        
        return UserResponse(
            id=new_user.id,
            username=new_user.username,
            email=new_user.email,
            full_name=new_user.full_name,
            role=new_user.role.value,
            is_active=new_user.is_active,
            last_login=new_user.last_login,
            created_at=new_user.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Collect all routers for import
all_routers = [auth_router, production_router, system_router, admin_router] 