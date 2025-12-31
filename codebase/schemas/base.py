from typing import Any, Optional
from pydantic import BaseModel


class BaseResponse(BaseModel):
    """Base response model"""
    success: bool = True
    message: Optional[str] = None


class SuccessResponse(BaseResponse):
    """Success response with data"""
    data: Any


class ErrorResponse(BaseResponse):
    """Error response model"""
    success: bool = False
    error: str
    details: Optional[Any] = None


class PaginatedResponse(BaseResponse):
    """Paginated response model"""
    data: list[Any]
    total: int
    page: int
    size: int
    pages: int