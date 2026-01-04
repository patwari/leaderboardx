"""
Logging configuration module.

Provides structured logging setup for development and production environments.
Configures appropriate log levels, formatters, and handlers based on environment.
"""

import logging
import sys
from typing import Optional
from codebase.config import settings


def setup_logging() -> None:
    """Configure application logging based on environment settings."""
    
    # Set log level based on debug mode
    log_level: int = logging.DEBUG if settings.debug else logging.INFO
    
    # Create formatter for structured logging
    formatter: logging.Formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Configure root logger
    root_logger: logging.Logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove any existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler for all environments
    console_handler: logging.StreamHandler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    
    # Add console handler
    root_logger.addHandler(console_handler)
    
    # Configure third-party library log levels
    _configure_third_party_loggers()
    
    # Log the configuration
    logger: logging.Logger = logging.getLogger(__name__)
    logger.info(f"Logging configured - Level: {logging.getLevelName(log_level)}")
    logger.info(f"Environment: {'development' if settings.debug else 'production'}")


def _configure_third_party_loggers() -> None:
    """Configure log levels for third-party libraries to reduce noise."""
    
    # Set uvicorn to INFO level (reduce debug noise)
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    
    # Set SQLAlchemy to WARNING level (reduce query logs)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    # Set httpx to WARNING level (for external API calls)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    # Set asyncio to WARNING level (reduce event loop noise)
    logging.getLogger("asyncio").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name.
    
    Args:
        name: Logger name, typically __name__ from calling module
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)