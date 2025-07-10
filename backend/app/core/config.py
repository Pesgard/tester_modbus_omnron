"""
Configuration management for the production system.
"""
import os
from typing import List
from dataclasses import dataclass


@dataclass
class Settings:
    """Application settings with environment variable support."""
    
    # Database configuration
    database_url: str = "postgresql+asyncpg://postgres:admin@localhost:5432/production_system"
    database_pool_size: int = 10
    database_echo: bool = False 
    
    # Modbus server configuration
    modbus_host: str = "0.0.0.0"
    modbus_port: int = 502
    
    # API configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_title: str = "Production System API"
    api_version: str = "2.0.0"
    
    # CORS configuration
    cors_origins: List[str] = None  # type: ignore
    
    # Logging configuration
    log_level: str = "INFO"
    log_file: str = "production_system.log"
    
    # Data processing configuration
    data_buffer_size: int = 1000
    batch_id_prefix: str = "BATCH"
    
    # WebSocket configuration
    websocket_max_connections: int = 100
    
    # Development/Debug flags
    debug: bool = False
    
    # Security configuration
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    def __post_init__(self):
        """Initialize default values and load from environment."""
        if self.cors_origins is None:
            self.cors_origins = ["*"]
        
        # Load from environment variables
        self.database_url = os.getenv("DATABASE_URL", self.database_url)
        self.database_pool_size = int(os.getenv("DATABASE_POOL_SIZE", str(self.database_pool_size)))
        self.database_echo = os.getenv("DATABASE_ECHO", "false").lower() in ("true", "1", "yes", "on")
        self.modbus_host = os.getenv("MODBUS_HOST", self.modbus_host)
        self.modbus_port = int(os.getenv("MODBUS_PORT", str(self.modbus_port)))
        self.api_host = os.getenv("API_HOST", self.api_host)
        self.api_port = int(os.getenv("API_PORT", str(self.api_port)))
        self.api_title = os.getenv("API_TITLE", self.api_title)
        self.api_version = os.getenv("API_VERSION", self.api_version)
        self.log_level = os.getenv("LOG_LEVEL", self.log_level)
        self.log_file = os.getenv("LOG_FILE", self.log_file)
        self.data_buffer_size = int(os.getenv("DATA_BUFFER_SIZE", str(self.data_buffer_size)))
        self.batch_id_prefix = os.getenv("BATCH_ID_PREFIX", self.batch_id_prefix)
        self.websocket_max_connections = int(os.getenv("WEBSOCKET_MAX_CONNECTIONS", str(self.websocket_max_connections)))
        self.debug = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes", "on")
        self.secret_key = os.getenv("SECRET_KEY", self.secret_key)
        self.algorithm = os.getenv("ALGORITHM", self.algorithm)
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", str(self.access_token_expire_minutes)))
        
        # Handle CORS origins as comma-separated string
        cors_env = os.getenv("CORS_ORIGINS")
        if cors_env:
            self.cors_origins = [origin.strip() for origin in cors_env.split(",")]


# Global settings instance
settings = Settings() 