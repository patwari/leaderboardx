from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from codebase.database import get_db, check_db_health
from codebase.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.version
    }


@router.get("/health/db")
async def database_health_check():
    """Database connectivity health check"""
    db_healthy = await check_db_health()
    
    status_code = 200 if db_healthy else 503
    
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "database": "connected" if db_healthy else "disconnected"
    }