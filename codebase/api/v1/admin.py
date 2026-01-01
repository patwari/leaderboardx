from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from codebase.database import get_db
from codebase.models import Company, Game, Leaderboard, Player, ScoreEvent
from codebase.schemas.admin import AdminOverview


router = APIRouter(tags=["admin"])


@router.get("/admin/overview", response_model=AdminOverview)
async def admin_overview(db: AsyncSession = Depends(get_db)):
    # No auth yet (you said you haven't deployed). Add auth before going public.
    companies = int((await db.execute(select(func.count()).select_from(Company))).scalar_one())
    games = int((await db.execute(select(func.count()).select_from(Game))).scalar_one())
    leaderboards = int((await db.execute(select(func.count()).select_from(Leaderboard))).scalar_one())
    players = int((await db.execute(select(func.count()).select_from(Player))).scalar_one())
    score_events = int((await db.execute(select(func.count()).select_from(ScoreEvent))).scalar_one())
    return AdminOverview(
        companies=companies,
        games=games,
        leaderboards=leaderboards,
        players=players,
        score_events=score_events,
    )
