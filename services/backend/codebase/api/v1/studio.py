from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from codebase.database import get_db
from codebase.crud.company import create_company, get_company
from codebase.crud.game import create_game, get_game
from codebase.crud.leaderboard import create_leaderboard, get_leaderboard
from codebase.models import Company, Game
from codebase.schemas.studio import (
    CompanyCreate,
    CompanyCreated,
    CompanySummary,
    GameCreate,
    GameCreated,
    LeaderboardCreate,
    LeaderboardCreated,
)


router = APIRouter(tags=["studio"])


@router.post("/studio/companies", response_model=CompanyCreated)
async def register_company(payload: CompanyCreate, db: AsyncSession = Depends(get_db)):
    company = await create_company(db, name=payload.name)
    return CompanyCreated(company_id=company.company_id, company_secret=company.company_secret, name=company.name)


@router.post("/studio/games", response_model=GameCreated)
async def register_game(payload: GameCreate, db: AsyncSession = Depends(get_db)):
    company = await get_company(db, payload.company_id, payload.company_secret)
    if company is None:
        raise HTTPException(status_code=401, detail="Invalid company credentials")

    game = await create_game(db, company_id=company.company_id, name=payload.name)
    return GameCreated(game_id=game.game_id, game_secret=game.game_secret, company_id=game.company_id, name=game.name)


@router.post("/studio/leaderboards", response_model=LeaderboardCreated)
async def register_leaderboard(payload: LeaderboardCreate, db: AsyncSession = Depends(get_db)):
    # Verify company auth + game ownership
    company = await get_company(db, payload.company_id, payload.company_secret)
    if company is None:
        raise HTTPException(status_code=401, detail="Invalid company credentials")

    game = await get_game(db, payload.game_id, company_id=company.company_id)
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found for this company")

    existing = await get_leaderboard(db, game_id=game.game_id, leaderboard_id=payload.leaderboard_id)
    if existing is not None:
        raise HTTPException(status_code=409, detail="leaderboard_id already exists for this game")

    lb = await create_leaderboard(
        db,
        game_id=game.game_id,
        leaderboard_id=payload.leaderboard_id,
        name=payload.name,
        sort_order=payload.sort_order,
    )
    return LeaderboardCreated(
        leaderboard_pk=lb.leaderboard_pk,
        game_id=lb.game_id,
        leaderboard_id=lb.leaderboard_id,
        name=lb.name,
        sort_order=lb.sort_order,
    )


@router.get("/studio/company", response_model=CompanySummary)
async def get_company_summary(company_id: str, company_secret: str, db: AsyncSession = Depends(get_db)):
    # lightweight summary for future dashboard wiring
    company = await get_company(db, company_id, company_secret)
    if company is None:
        raise HTTPException(status_code=401, detail="Invalid company credentials")

    # Load games + leaderboards for basic dashboard wiring
    res = await db.execute(
        select(Company)
        .options(selectinload(Company.games).selectinload(Game.leaderboards))
        .where(Company.company_id == company.company_id)
    )
    company_full = res.scalar_one()

    return CompanySummary(
        company_id=company_full.company_id,
        name=company_full.name,
        games=[
            {
                "game_id": g.game_id,
                "name": g.name,
                "leaderboards": [
                    {"leaderboard_id": lb.leaderboard_id, "name": lb.name, "sort_order": lb.sort_order}
                    for lb in getattr(g, "leaderboards", [])
                ],
            }
            for g in getattr(company_full, "games", [])
        ],
    )
