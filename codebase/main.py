"""
LeaderboardX - FastAPI Application

Multi-tenant SaaS leaderboard platform for indie game studios.
"""

import logging
from typing import Dict, Union, Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from codebase.config import settings
from codebase.logging_config import setup_logging
from codebase.api.v1.health import router as health_router
from codebase.api.v1.users import router as users_router
from codebase.api.v1.leaderboards import router as leaderboards_router

# Initialize logging first
setup_logging()
logger: logging.Logger = logging.getLogger(__name__)

# Initialize FastAPI fast_app with configuration
fast_app: FastAPI = FastAPI(
    title=settings.app_name,
    description="High-performance, multi-tenant leaderboard platform for indie game studios",
    version=settings.version,
    debug=settings.debug,
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
)

# Add CORS middleware for frontend integration
fast_app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Include API routers
fast_app.include_router(health_router, prefix="/api/v1")
fast_app.include_router(users_router, prefix="/api/v1")
fast_app.include_router(leaderboards_router, prefix="/api/v1")


@fast_app.on_event("startup")
async def startup_event() -> None:
    """Application startup event handler."""
    logger.info(f"Starting {settings.app_name}")
    logger.info(f"Environment: {'development' if settings.is_development else 'production'}")
    logger.info(f"Debug mode: {settings.debug}")


@fast_app.on_event("shutdown")
async def shutdown_event() -> None:
    """Application shutdown event handler."""
    logger.info(f"Shutting down {settings.app_name}")
