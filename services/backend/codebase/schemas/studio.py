from typing import Optional, Literal
from uuid import UUID

from pydantic import BaseModel, Field


LeaderboardId = str
DeviceId = str


class CompanyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)


class CompanyCreated(BaseModel):
    company_id: UUID
    company_secret: str
    name: str


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


class CompanyUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    rotate_secret: bool = False
    company_id: UUID
    company_secret: str = Field(..., min_length=16, max_length=64)
