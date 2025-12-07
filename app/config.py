"""
Application configuration management using Pydantic Settings.
Loads configuration from environment variables with sensible defaults.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Attributes:
        database_url: PostgreSQL connection string
        secret_key: JWT secret key for token signing
        algorithm: JWT algorithm (default: HS256)
        access_token_expire_minutes: JWT token expiration time
        api_port: Port for FastAPI server (default: 8500)
        api_host: Host for FastAPI server (default: 0.0.0.0)
    """
    
    # Database Configuration
    database_url: str = "postgresql://postgres:postgres@db:5432/course_registration"
    
    # JWT Configuration
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # API Configuration
    api_port: int = 8500
    api_host: str = "0.0.0.0"
    
    # Environment
    environment: str = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

