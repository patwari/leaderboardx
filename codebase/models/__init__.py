"""SQLAlchemy models.

This codebase is intentionally multi-tenant:
Company -> Games -> Leaderboards -> Players -> Scores.
"""

from codebase.database import Base
from codebase.models.company import Company
from codebase.models.game import Game
from codebase.models.leaderboard import Leaderboard
from codebase.models.player import Player
from codebase.models.score import BestScore, ScoreEvent

__all__ = [
    "Base",
    "Company",
    "Game",
    "Leaderboard",
    "Player",
    "BestScore",
    "ScoreEvent",
]
