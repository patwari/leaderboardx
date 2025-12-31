from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, validator
import re


class UserBase(BaseModel):
    """Base User model"""
    device_id: str = Field(..., min_length=1, max_length=255, description="Device ID provided by the game")
    
    @validator('device_id')
    def validate_device_id(cls, v):
        if not re.match(r'^[A-Za-z0-9\-]+$', v):
            raise ValueError('Device ID can only contain A-Z, a-z, 0-9, and - characters')
        return v


class UserCreate(UserBase):
    """User creation model"""
    pass


class UserUpdate(BaseModel):
    """User update model"""
    device_id: Optional[str] = Field(None, min_length=1, max_length=255, description="Device ID provided by the game")
    
    @validator('device_id')
    def validate_device_id(cls, v):
        if v is not None and not re.match(r'^[A-Za-z0-9\-]+$', v):
            raise ValueError('Device ID can only contain A-Z, a-z, 0-9, and - characters')
        return v


class UserResponse(UserBase):
    """User response model"""
    xid: UUID = Field(..., description="LeaderboardX internal user ID")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        populate_by_name = True


class UserListResponse(BaseModel):
    """User list response model"""
    users: list[UserResponse]
    total: int
    page: int
    size: int