"""
Application configuration module.

Reads configuration from environment variables for Docker-first deployment.
All settings use environment variables with sensible defaults for development.
"""

import os
from typing import Optional


class Settings:
    """Application settings loaded from environment variables."""
    
    def __init__(self) -> None:
        # Core application settings
        self.app_name: str = os.environ["APP_NAME"]
        self.version: str = os.environ["APP_VERSION"]
        self.debug: bool = os.environ["DEBUG"].lower() == "true"
        
        # Database configuration
        self.database_url: str = os.environ["DATABASE_URL"]
        
        # Redis configuration
        self.redis_url: str = os.environ["REDIS_URL"]
        
        # API settings
        self.api_v1_prefix: str = "/api/v1"
        
        # Security settings
        self.allowed_hosts: list[str] = self._parse_hosts(os.environ["ALLOWED_HOSTS"])
        
        # CORS settings for frontend integration
        self.cors_origins: list[str] = self._parse_hosts(os.environ["CORS_ORIGINS"])
    
    def _parse_hosts(self, hosts_str: str) -> list[str]:
        """Parse comma-separated host list."""
        return [host.strip() for host in hosts_str.split(",") if host.strip()]
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.debug
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return not self.debug


# Global settings instance
settings = Settings()
