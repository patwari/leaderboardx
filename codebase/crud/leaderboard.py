from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from codebase.models import Leaderboard


async def create_leaderboard(
    db: AsyncSession,
    *,
    game_id,
    leaderboard_id: str,
    name: str | None,
    sort_order: str,
) -> Leaderboard:
    lb = Leaderboard(
        game_id=game_id,
        leaderboard_id=leaderboard_id,
        name=name,
        sort_order=sort_order,
    )
    db.add(lb)
    await db.commit()
    await db.refresh(lb)
    return lb


async def get_leaderboard(db: AsyncSession, *, game_id, leaderboard_id: str) -> Leaderboard | None:
    stmt = select(Leaderboard).where(
        Leaderboard.game_id == game_id,
        Leaderboard.leaderboard_id == leaderboard_id,
    )
    res = await db.execute(stmt)
    return res.scalar_one_or_none()