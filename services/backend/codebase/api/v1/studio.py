from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from codebase.database import get_db
from codebase.crud.company import (
    create_company,
    get_company_by_id,
    get_company_by_login,
    update_company,
    verify_password,
)
from codebase.crud.game import create_game, get_game
from codebase.crud.leaderboard import create_leaderboard, get_leaderboard
from codebase.models import Company, Game
from codebase.schemas.studio import (
    CompanyCreate,
    CompanyCreated,
    CompanySummary,
    CompanyUpdate,
    StudioAuth,
    StudioLogin,
    GameCreate,
    GameCreated,
    LeaderboardCreate,
    LeaderboardCreated,
)


router = APIRouter(tags=["studio"])


@router.post("/studio/companies", response_model=CompanyCreated)
async def register_company(payload: CompanyCreate, db: AsyncSession = Depends(get_db)):
    existing = await get_company_by_login(db, payload.login_id)
    if existing is not None:
        raise HTTPException(status_code=409, detail="login_id already exists")
    company = await create_company(db, name=payload.name, login_id=payload.login_id, password=payload.password)
    return CompanyCreated(studio_id=company.company_id, login_id=company.login_id, name=company.name)


@router.post("/studio/login", response_model=CompanySummary)
async def login_company(payload: StudioLogin, db: AsyncSession = Depends(get_db)):
    company = await get_company_by_login(db, payload.login_id)
    if company is None or not verify_password(payload.password, company.password_hash):
        raise HTTPException(status_code=401, detail="Invalid login credentials")
    return await _company_summary(db, company)


@router.post("/studio/games", response_model=GameCreated)
async def register_game(payload: GameCreate, db: AsyncSession = Depends(get_db)):
    company = await get_company_by_id(db, payload.studio_id)
    if company is None or not verify_password(payload.password, company.password_hash):
        raise HTTPException(status_code=401, detail="Invalid studio credentials")

    game = await create_game(db, company_id=company.company_id, name=payload.name)
    return GameCreated(game_id=game.game_id, game_secret=game.game_secret, studio_id=game.company_id, name=game.name)


@router.post("/studio/leaderboards", response_model=LeaderboardCreated)
async def register_leaderboard(payload: LeaderboardCreate, db: AsyncSession = Depends(get_db)):
    # Verify studio auth + game ownership
    company = await get_company_by_id(db, payload.studio_id)
    if company is None or not verify_password(payload.password, company.password_hash):
        raise HTTPException(status_code=401, detail="Invalid studio credentials")

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


@router.post("/studio/summary", response_model=CompanySummary)
async def get_company_summary(payload: StudioAuth, db: AsyncSession = Depends(get_db)):
    company = await get_company_by_id(db, payload.studio_id)
    if company is None or not verify_password(payload.password, company.password_hash):
        raise HTTPException(status_code=401, detail="Invalid studio credentials")
    return await _company_summary(db, company)


@router.post("/studio/company/update", response_model=CompanyCreated)
async def update_company_settings(payload: CompanyUpdate, db: AsyncSession = Depends(get_db)):
    company = await get_company_by_id(db, payload.studio_id)
    if company is None or not verify_password(payload.current_password, company.password_hash):
        raise HTTPException(status_code=401, detail="Invalid studio credentials")

    updated = await update_company(
        db,
        company,
        name=payload.name or company.name,
        login_id=payload.login_id or company.login_id,
        password=payload.password,
    )
    return CompanyCreated(studio_id=updated.company_id, login_id=updated.login_id, name=updated.name)


async def _company_summary(db: AsyncSession, company: Company) -> CompanySummary:
    res = await db.execute(
        select(Company)
        .options(selectinload(Company.games).selectinload(Game.leaderboards))
        .where(Company.company_id == company.company_id)
    )
    company_full = res.scalar_one()

    return CompanySummary(
        studio_id=company_full.company_id,
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
