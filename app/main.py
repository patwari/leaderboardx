"""
LeaderboardX - FastAPI Application

Multi-tenant SaaS leaderboard platform for indie game studios.
"""

from typing import Dict, Union, Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

# Initialize FastAPI app with configuration
app: FastAPI = FastAPI(
    title=settings.app_name,
    description="High-performance, multi-tenant leaderboard platform for indie game studios",
    version="1.0.0",
    debug=settings.debug,
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> Dict[str, Union[str, bool]]:
    """Health check endpoint for monitoring and load balancers."""
    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": "development" if settings.is_development else "production"
    }
