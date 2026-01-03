from typing import Optional, Literal
from uuid import UUID

from pydantic import BaseModel, Field


LeaderboardId = str
DeviceId = str


class CompanyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    username: str = Field(..., min_length=1, max_length=50, pattern=r"^[a-z0-9\-]+$")
    password: str = Field(..., min_length=6, max_length=128)


class CompanyCreated(BaseModel):
    company_id: UUID
    company_secret: str
    name: str
    username: str


class StudioAuth(BaseModel):
    company_id: UUID
    company_secret: str = Field(..., min_length=16, max_length=64)


class GameCreate(StudioAuth):
    name: str = Field(..., min_length=1, max_length=200)


class GameCreated(BaseModel):
    game_id: UUID
    game_secret: str
    company_id: UUID
    name: str


class LeaderboardCreate(StudioAuth):
    game_id: UUID
    leaderboard_id: LeaderboardId = Field(..., min_length=1, max_length=64, pattern=r"^[A-Za-z0-9\-]+$")
    name: Optional[str] = Field(default=None, max_length=200)
    sort_order: Literal["asc", "desc"] = "desc"


class LeaderboardCreated(BaseModel):
    leaderboard_pk: UUID
    game_id: UUID
    leaderboard_id: str
    name: Optional[str] = None
    sort_order: Literal["asc", "desc"]


class LeaderboardSummary(BaseModel):
    leaderboard_id: str
    name: Optional[str] = None
    sort_order: Literal["asc", "desc"]


class GameSummary(BaseModel):
    game_id: UUID
    name: str
    leaderboards: list[LeaderboardSummary] = []


class CompanySummary(BaseModel):
    company_id: UUID
    name: str
    games: list[GameSummary] = []
