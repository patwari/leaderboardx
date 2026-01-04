from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from codebase.models import BestScore, Leaderboard, Player, ScoreEvent


async def submit_score(
    db: AsyncSession,
    *,
    game_id,
    xid,
    leaderboard_id: str,
    value: int,
) -> tuple[Leaderboard, int, bool]:
    """Submit a score.

    Returns (leaderboard, best_value, updated).
    """
    async with db.begin():
        # Verify player belongs to game
        res_player = await db.execute(
            select(Player).where(Player.xid == xid, Player.game_id == game_id)
        )
        player = res_player.scalar_one_or_none()
        if player is None:
            raise ValueError("Unknown player for this game")

        # Get or auto-create leaderboard (client-driven creation is allowed for now)
        res_lb = await db.execute(
            select(Leaderboard).where(
                Leaderboard.game_id == game_id,
                Leaderboard.leaderboard_id == leaderboard_id,
            )
        )
        lb = res_lb.scalar_one_or_none()
        if lb is None:
            lb = Leaderboard(game_id=game_id, leaderboard_id=leaderboard_id, name=None, sort_order="desc")
            db.add(lb)
            await db.flush()  # assign leaderboard_pk

        # Write event history
        db.add(ScoreEvent(leaderboard_pk=lb.leaderboard_pk, player_xid=player.xid, value=value))

        # Upsert best score
        res_best = await db.execute(
            select(BestScore).where(
                BestScore.leaderboard_pk == lb.leaderboard_pk,
                BestScore.player_xid == player.xid,
            )
        )
        best = res_best.scalar_one_or_none()

        updated = False
        if best is None:
            best = BestScore(leaderboard_pk=lb.leaderboard_pk, player_xid=player.xid, best_value=value)
            db.add(best)
            updated = True
        else:
            if lb.sort_order == "desc":
                if value > best.best_value:
                    best.best_value = value
                    updated = True
            else:
                if value < best.best_value:
                    best.best_value = value
                    updated = True

        await db.flush()

    # After the transaction, refresh computed state
    await db.refresh(lb)
    if best is not None:
        await db.refresh(best)
    return lb, best.best_value, updated


async def fetch_leaderboard(
    db: AsyncSession,
    *,
    game_id,
    leaderboard_id: str,
    limit: int = 50,
    offset: int = 0,
    xid=None,
) -> dict:
    """Fetch leaderboard entries + optional rank for a given player."""

    res_lb = await db.execute(
        select(Leaderboard).where(
            Leaderboard.game_id == game_id,
            Leaderboard.leaderboard_id == leaderboard_id,
        )
    )
    lb = res_lb.scalar_one_or_none()
    if lb is None:
        raise ValueError("Leaderboard not found")

    # Total
    res_total = await db.execute(
        select(func.count()).select_from(BestScore).where(BestScore.leaderboard_pk == lb.leaderboard_pk)
    )
    total = int(res_total.scalar_one())

    order = BestScore.best_value.desc() if lb.sort_order == "desc" else BestScore.best_value.asc()

    rank_expr = func.rank().over(order_by=order).label("rank")
    stmt = (
        select(rank_expr, BestScore.player_xid, BestScore.best_value, BestScore.updated_at)
        .where(BestScore.leaderboard_pk == lb.leaderboard_pk)
        .order_by(order)
        .offset(offset)
        .limit(limit)
    )
    res = await db.execute(stmt)
    rows = res.all()

    entries = [
        {
            "rank": int(r.rank),
            "xid": r.player_xid,
            "best_value": int(r.best_value),
            "updated_at": r.updated_at.isoformat() if r.updated_at is not None else "",
        }
        for r in rows
    ]

    your_rank = None
    your_best_value = None

    if xid is not None:
        # Ensure player belongs to game
        res_player = await db.execute(select(Player.xid).where(Player.xid == xid, Player.game_id == game_id))
        if res_player.scalar_one_or_none() is not None:
            subq = (
                select(
                    BestScore.player_xid.label("player_xid"),
                    BestScore.best_value.label("best_value"),
                    func.rank().over(order_by=order).label("rank"),
                )
                .where(BestScore.leaderboard_pk == lb.leaderboard_pk)
                .subquery()
            )
            res_you = await db.execute(select(subq.c.rank, subq.c.best_value).where(subq.c.player_xid == xid))
            you = res_you.first()
            if you:
                your_rank = int(you.rank)
                your_best_value = int(you.best_value)

    return {
        "leaderboard": lb,
        "total": total,
        "entries": entries,
        "your_rank": your_rank,
        "your_best_value": your_best_value,
    }