from typing import Optional, Literal
from uuid import UUID

from pydantic import BaseModel, Field


LeaderboardId = str
DeviceId = str


class CompanyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    login_id: str = Field(..., min_length=3, max_length=64, pattern=r"^[a-z0-9\-]+$")
    password: str = Field(..., min_length=6, max_length=128)


class CompanyCreated(BaseModel):
    studio_id: UUID
    login_id: str
    name: str


class StudioLogin(BaseModel):
    login_id: str = Field(..., min_length=3, max_length=64, pattern=r"^[a-z0-9\-]+$")
    password: str = Field(..., min_length=6, max_length=128)


class StudioAuth(BaseModel):
    studio_id: UUID
    password: str = Field(..., min_length=6, max_length=128)


class GameCreate(StudioAuth):
    name: str = Field(..., min_length=1, max_length=200)


class GameCreated(BaseModel):
    game_id: UUID
    game_secret: str
    studio_id: UUID
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
    studio_id: UUID
    name: str
    games: list[GameSummary] = []


class CompanyUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    login_id: Optional[str] = Field(default=None, min_length=3, max_length=64, pattern=r"^[a-z0-9\-]+$")
    password: Optional[str] = Field(default=None, min_length=6, max_length=128)
    studio_id: UUID
    current_password: str = Field(..., min_length=6, max_length=128)
