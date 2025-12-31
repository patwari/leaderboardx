from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field


class LeaderboardBase(BaseModel):
    """Base Leaderboard model"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    is_active: bool = True
    settings: dict[str, Any] = Field(default_factory=dict)


class LeaderboardCreate(LeaderboardBase):
    """Leaderboard creation model"""
    pass


class LeaderboardUpdate(BaseModel):
    """Leaderboard update model"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_active: Optional[bool] = None
    settings: Optional[dict[str, Any]] = None


class LeaderboardResponse(LeaderboardBase):
    """Leaderboard response model"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class LeaderboardListResponse(BaseModel):
    """Leaderboard list response model"""
    leaderboards: list[LeaderboardResponse]
    total: int
    page: int
    size: int