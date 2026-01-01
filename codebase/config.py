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
        self.app_name: str = os.environ.get("APP_NAME", "LeaderboardX")
        self.version: str = os.environ.get("APP_VERSION", "0.0.1")
        self.debug: bool = os.environ.get("DEBUG", "false").lower() == "true"
        self.secret_key: str = os.environ.get("SECRET_KEY", "WgEPVP24jDgvDQYK")
        
        # Database configuration
        self.database_url: str = os.environ.get(
            "DATABASE_URL", 
            "postgresql+asyncpg://user:pass@localhost:5432/leaderboardx-db"
        )
        
        # Redis configuration
        self.redis_url: str = os.environ.get("REDIS_URL", "redis://localhost:6379")
        
        # API settings
        self.api_v1_prefix: str = "/api/v1"

        # Admin dashboard (HTML) settings
        # Use a different base path than the API. Example: /__admin
        self.admin_dashboard_path: str = os.environ.get("ADMIN_DASHBOARD_PATH", "/__admin")
        # Simple shared token for now. Provide in header `X-Admin-Token` or query `token`.
        # In production you should set this explicitly.
        self.admin_token: str = os.environ.get("ADMIN_TOKEN", "")
        
        # Security settings
        self.allowed_hosts: list[str] = self._parse_hosts(
            os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1")
        )
        
        # CORS settings for frontend integration
        self.cors_origins: list[str] = self._parse_hosts(
            os.environ.get("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000")
        )
    
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