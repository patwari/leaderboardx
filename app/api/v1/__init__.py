from fastapi import APIRouter
from app.config import settings

v1_router = APIRouter(prefix=settings.api_v1_prefix)

__all__ = ["v1_router"]