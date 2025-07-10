"""
Authentication and authorization service.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List
from jose import JWTError, jwt
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ...core.config import settings
from ...infrastructure.database.repository import UserRepository, AuditLogRepository
from ...infrastructure.database.models import User, UserRole

security = HTTPBearer()


class AuthService:
    """Service for authentication and authorization."""
    
    def __init__(self, user_repo: UserRepository, audit_repo: AuditLogRepository):
        self.user_repo = user_repo
        self.audit_repo = audit_repo
    
    async def authenticate_user(self, username: str, password: str, 
                               ip_address: Optional[str] = None,
                               user_agent: Optional[str] = None) -> Optional[User]:
        """Authenticate a user with username and password."""
        user = await self.user_repo.get_user_by_username(username)
        if not user:
            await self.audit_repo.log_action(
                user_id=None,
                action="login_failed",
                resource="auth",
                ip_address=ip_address,
                user_agent=user_agent,
                details={"username": username, "reason": "user_not_found"}
            )
            return None
        
        if not user.is_active:
            await self.audit_repo.log_action(
                user_id=user.id,
                action="login_failed",
                resource="auth",
                ip_address=ip_address,
                user_agent=user_agent,
                details={"username": username, "reason": "user_inactive"}
            )
            return None
        
        if not await self.user_repo.verify_password(password, user.hashed_password):
            await self.audit_repo.log_action(
                user_id=user.id,
                action="login_failed",
                resource="auth",
                ip_address=ip_address,
                user_agent=user_agent,
                details={"username": username, "reason": "invalid_password"}
            )
            return None
        
        # Update last login
        await self.user_repo.update_last_login(user.id)
        
        # Log successful login
        await self.audit_repo.log_action(
            user_id=user.id,
            action="login_success",
            resource="auth",
            ip_address=ip_address,
            user_agent=user_agent,
            details={"username": username}
        )
        
        return user
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt
    
    async def get_current_user(self, credentials: HTTPAuthorizationCredentials) -> User:
        """Get current user from JWT token."""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = jwt.decode(credentials.credentials, settings.secret_key, algorithms=[settings.algorithm])
            user_id = payload.get("sub")
            if user_id is None:
                raise credentials_exception
            user_id = int(user_id)
        except JWTError:
            raise credentials_exception
        
        user = await self.user_repo.get_user_by_id(user_id)
        if user is None:
            raise credentials_exception
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user"
            )
        
        return user
    
    def check_permission(self, user: User, resource: str, action: str) -> bool:
        """Check if user has permission for resource and action."""
        # Admin has all permissions
        if user.role == UserRole.ADMIN:
            return True
        
        # Check role-based permissions
        role_permissions = {
            UserRole.SUPERVISOR: {
                "production": ["read", "write"],
                "system": ["read"],
                "users": ["read"]
            },
            UserRole.OPERATOR: {
                "production": ["read", "write"],
                "system": ["read"]
            },
            UserRole.VIEWER: {
                "production": ["read"],
                "system": ["read"]
            }
        }
        
        user_perms = role_permissions.get(user.role, {})
        allowed_actions = user_perms.get(resource, [])
        
        if action in allowed_actions:
            return True
        
        # Check specific permissions
        for permission in user.permissions:
            if permission.resource == resource and permission.action == action:
                return True
        
        return False
    
    def require_permission(self, resource: str, action: str):
        """Decorator to require specific permission."""
        def decorator(func):
            async def wrapper(*args, **kwargs):
                # Extract user from kwargs or request
                user = kwargs.get('current_user')
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Authentication required"
                    )
                
                if not self.check_permission(user, resource, action):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Insufficient permissions for {resource}.{action}"
                    )
                
                return await func(*args, **kwargs)
            return wrapper
        return decorator
    
    def require_role(self, min_role: UserRole):
        """Decorator to require minimum role level."""
        role_hierarchy = {
            UserRole.VIEWER: 1,
            UserRole.OPERATOR: 2,
            UserRole.SUPERVISOR: 3,
            UserRole.ADMIN: 4
        }
        
        def decorator(func):
            async def wrapper(*args, **kwargs):
                user = kwargs.get('current_user')
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Authentication required"
                    )
                
                user_level = role_hierarchy.get(user.role, 0)
                required_level = role_hierarchy.get(min_role, 999)
                
                if user_level < required_level:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Insufficient role level. Required: {min_role.value}"
                    )
                
                return await func(*args, **kwargs)
            return wrapper
        return decorator 