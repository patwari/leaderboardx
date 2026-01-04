from pydantic import BaseModel


class AdminOverview(BaseModel):
    companies: int
    games: int
    leaderboards: int
    players: int
    score_events: int