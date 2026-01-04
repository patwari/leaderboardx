from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from codebase.database import get_db
from codebase.crud.game import get_game
from codebase.crud.player import get_or_create_player
from codebase.crud.scores import fetch_leaderboard, submit_score
from codebase.schemas.client import (
    ClientAuthRequest,
    ClientAuthResponse,
    LeaderboardResponse,
    ScoreSubmitRequest,
    ScoreSubmitResponse,
)


router = APIRouter(tags=["client"])


@router.post("/client/auth", response_model=ClientAuthResponse)
async def client_auth(payload: ClientAuthRequest, db: AsyncSession = Depends(get_db)):
    game = await get_game(db, payload.game_id)
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found")

    player, is_new = await get_or_create_player(db, game_id=payload.game_id, device_id=payload.device_id)
    return ClientAuthResponse(game_id=payload.game_id, xid=player.xid, is_new=is_new)


@router.post("/client/score", response_model=ScoreSubmitResponse)
async def client_submit_score(payload: ScoreSubmitRequest, db: AsyncSession = Depends(get_db)):
    try:
        lb, best_value, updated = await submit_score(
            db,
            game_id=payload.game_id,
            xid=payload.xid,
            leaderboard_id=payload.leaderboard_id,
            value=payload.value,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return ScoreSubmitResponse(
        game_id=payload.game_id,
        leaderboard_id=lb.leaderboard_id,
        xid=payload.xid,
        best_value=best_value,
        updated=updated,
    )


@router.get("/client/leaderboard", response_model=LeaderboardResponse)
async def client_get_leaderboard(
    game_id: UUID,
    leaderboard_id: str,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    xid: UUID | None = None,
    db: AsyncSession = Depends(get_db),
):
    try:
        data = await fetch_leaderboard(
            db,
            game_id=game_id,
            leaderboard_id=leaderboard_id,
            limit=limit,
            offset=offset,
            xid=xid,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    lb = data["leaderboard"]
    return LeaderboardResponse(
        game_id=lb.game_id,
        leaderboard_id=lb.leaderboard_id,
        sort_order=lb.sort_order,
        total=data["total"],
        entries=data["entries"],
        your_rank=data["your_rank"],
        your_best_value=data["your_best_value"],
    )
