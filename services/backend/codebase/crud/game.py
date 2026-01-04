import secrets
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from codebase.models import Game


def _new_secret() -> str:
    return secrets.token_urlsafe(32)


async def create_game(db: AsyncSession, company_id, name: str) -> Game:
    game = Game(company_id=company_id, name=name, game_secret=_new_secret())
    db.add(game)
    await db.commit()
    await db.refresh(game)
    return game


async def get_game(db: AsyncSession, game_id, *, company_id=None) -> Game | None:
    stmt = select(Game).where(Game.game_id == game_id)
    if company_id is not None:
        stmt = stmt.where(Game.company_id == company_id)
    res = await db.execute(stmt)
    return res.scalar_one_or_none()