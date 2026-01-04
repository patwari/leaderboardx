from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from codebase.models import Player


async def get_or_create_player(db: AsyncSession, *, game_id, device_id: str) -> tuple[Player, bool]:
    """Return (player, is_new)."""
    stmt = select(Player).where(Player.game_id == game_id, Player.device_id == device_id)
    res = await db.execute(stmt)
    player = res.scalar_one_or_none()
    if player is not None:
        return player, False

    player = Player(game_id=game_id, device_id=device_id)
    db.add(player)
    await db.commit()
    await db.refresh(player)
    return player, True