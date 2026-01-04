from typing import Optional
from fastapi import Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from codebase.database import get_db


class PaginationParams:
    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number"),
        size: int = Query(50, ge=1, le=100, description="Page size"),
    ):
        self.page = page
        self.size = size
        self.skip = (page - 1) * size
        self.limit = size


def get_pagination_params(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Page size"),
) -> PaginationParams:
    """Get pagination parameters"""
    return PaginationParams(page=page, size=size)


async def get_database() -> AsyncSession:
    """Get database session dependency"""
    async for session in get_db():
        yield session