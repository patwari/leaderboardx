from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field
from codebase.schemas.user import UserResponse
from codebase.schemas.leaderboard import LeaderboardResponse


class ScoreBase(BaseModel):
    """Base Score model"""
    value: Decimal = Field(..., ge=0, decimal_places=4)


class ScoreCreate(ScoreBase):
    """Score creation model"""
    user_xid: UUID
    leaderboard_id: int


class ScoreUpdate(BaseModel):
    """Score update model"""
    value: Optional[Decimal] = Field(None, ge=0, decimal_places=4)


class ScoreResponse(ScoreBase):
    """Score response model"""
    xid: UUID
    user_xid: UUID
    leaderboard_id: int
    submitted_at: datetime
    
    class Config:
        from_attributes = True


class ScoreWithDetailsResponse(ScoreResponse):
    """Score response with user and leaderboard details"""
    user: UserResponse
    leaderboard: LeaderboardResponse


class ScoreListResponse(BaseModel):
    """Score list response model"""
    scores: list[ScoreResponse]
    total: int
    page: int
    size: int


class LeaderboardRankingResponse(BaseModel):
    """Leaderboard ranking response"""
    rank: int
    user: UserResponse
    score: Decimal
    submitted_at: datetime