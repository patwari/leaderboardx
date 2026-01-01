from typing import Optional, Literal
from uuid import UUID

from pydantic import BaseModel, Field


class ClientAuthRequest(BaseModel):
    game_id: UUID
    device_id: str = Field(..., min_length=1, max_length=255, pattern=r"^[A-Za-z0-9\-]+$")


class ClientAuthResponse(BaseModel):
    game_id: UUID
    xid: UUID
    is_new: bool


class ScoreSubmitRequest(BaseModel):
    game_id: UUID
    xid: UUID
    leaderboard_id: str = Field(..., min_length=1, max_length=64, pattern=r"^[A-Za-z0-9\-]+$")
    value: int = Field(..., ge=-2_147_483_648, le=2_147_483_647)


class ScoreSubmitResponse(BaseModel):
    game_id: UUID
    leaderboard_id: str
    xid: UUID
    best_value: int
    updated: bool  # whether best score changed


class LeaderboardEntry(BaseModel):
    rank: int
    xid: UUID
    best_value: int
    updated_at: str


class LeaderboardResponse(BaseModel):
    game_id: UUID
    leaderboard_id: str
    sort_order: Literal["asc", "desc"]
    total: int
    entries: list[LeaderboardEntry]
    your_rank: Optional[int] = None
    your_best_value: Optional[int] = None