"""CRUD helpers (async SQLAlchemy)."""

from codebase.crud.company import create_company, get_company_by_id, get_company_by_login
from codebase.crud.game import create_game, get_game
from codebase.crud.leaderboard import create_leaderboard, get_leaderboard
from codebase.crud.player import get_or_create_player
from codebase.crud.scores import submit_score, fetch_leaderboard

__all__ = [
    "create_company",
    "get_company_by_id",
    "get_company_by_login",
    "create_game",
    "get_game",
    "create_leaderboard",
    "get_leaderboard",
    "get_or_create_player",
    "submit_score",
    "fetch_leaderboard",
]
