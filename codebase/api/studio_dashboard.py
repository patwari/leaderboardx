"""Studio HTML dashboard for company login and game management."""

from __future__ import annotations

import hmac
import os
from datetime import datetime, timedelta
from hashlib import sha256
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Form, HTTPException, Request, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from codebase.config import settings
from codebase.crud.company import create_company, get_company, get_company_by_username
from codebase.crud.game import create_game
from codebase.database import get_db
from codebase.models import BestScore, Company, Game, Leaderboard, Player, ScoreEvent
from codebase.security import verify_password


router = APIRouter(tags=["studio-dashboard"], include_in_schema=False)

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

SESSION_COOKIE = "studio_session"
SESSION_MAX_AGE_SECONDS = 30 * 24 * 3600  # 1 month


def _sign_session(company_id: str, expires_at: datetime) -> str:
    payload = f"{company_id}.{int(expires_at.timestamp())}"
    digest = hmac.new(settings.secret_key.encode("utf-8"), payload.encode("utf-8"), sha256).hexdigest()
    return f"{payload}.{digest}"


def _verify_session(token: str) -> Optional[str]:
    if not token:
        return None
    parts = token.split(".")
    if len(parts) != 3:
        return None
    company_id, exp_raw, signature = parts
    try:
        exp_ts = int(exp_raw)
    except ValueError:
        return None
    expected = hmac.new(settings.secret_key.encode("utf-8"), f"{company_id}.{exp_raw}".encode("utf-8"), sha256).hexdigest()
    if not hmac.compare_digest(signature, expected):
        return None
    if datetime.utcnow().timestamp() > exp_ts:
        return None
    return company_id


async def _get_company_from_request(request: Request, db: AsyncSession) -> Optional[Company]:
    cookie_value = request.cookies.get(SESSION_COOKIE, "")
    company_id = _verify_session(cookie_value)
    if not company_id:
        return None
    return await get_company(db, company_id)


@router.get("/", response_class=HTMLResponse)
async def studio_root(request: Request, db: AsyncSession = Depends(get_db)) -> HTMLResponse:
    company = await _get_company_from_request(request, db)
    if company:
        return RedirectResponse(url=f"{settings.studio_dashboard_path}/overview")
    return RedirectResponse(url=f"{settings.studio_dashboard_path}/login")


@router.get("/login", response_class=HTMLResponse)
async def studio_login_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "studio_login.html",
        {"request": request, "base": settings.studio_dashboard_path},
    )


@router.get("/register", response_class=HTMLResponse)
async def studio_register_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "studio_register.html",
        {"request": request, "base": settings.studio_dashboard_path},
    )


@router.post("/login", response_class=HTMLResponse)
async def studio_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db),
) -> HTMLResponse:
    company = await get_company_by_username(db, username.strip().lower())
    if not company or not verify_password(password, company.password_hash):
        return templates.TemplateResponse(
            "studio_login.html",
            {"request": request, "error": "Invalid username or password", "base": settings.studio_dashboard_path},
            status_code=401,
        )

    expires_at = datetime.utcnow() + timedelta(seconds=SESSION_MAX_AGE_SECONDS)
    token = _sign_session(str(company.company_id), expires_at)

    response = RedirectResponse(url=f"{settings.studio_dashboard_path}/overview", status_code=303)
    response.set_cookie(
        key=SESSION_COOKIE,
        value=token,
        httponly=True,
        secure=settings.is_production,
        samesite="lax",
        max_age=SESSION_MAX_AGE_SECONDS,
    )
    return response


@router.post("/register", response_class=HTMLResponse)
async def studio_register(
    request: Request,
    name: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db),
) -> HTMLResponse:
    username = username.strip()
    username = username.lower()
    name = name.strip()
    if not username or not name:
        return templates.TemplateResponse(
            "studio_register.html",
            {"request": request, "error": "Name and username are required", "base": settings.studio_dashboard_path},
            status_code=400,
        )
    if any(ch for ch in username if not (ch.isdigit() or ch == "-" or ("a" <= ch <= "z"))):
        return templates.TemplateResponse(
            "studio_register.html",
            {"request": request, "error": "Username must be a-z, 0-9, '-'", "base": settings.studio_dashboard_path},
            status_code=400,
        )

    existing = await get_company_by_username(db, username)
    if existing:
        return templates.TemplateResponse(
            "studio_register.html",
            {"request": request, "error": "Username already taken", "base": settings.studio_dashboard_path},
            status_code=409,
        )

    company = await create_company(db, name=name, username=username, password=password)

    expires_at = datetime.utcnow() + timedelta(seconds=SESSION_MAX_AGE_SECONDS)
    token = _sign_session(str(company.company_id), expires_at)

    response = RedirectResponse(url=f"{settings.studio_dashboard_path}/overview", status_code=303)
    response.set_cookie(
        key=SESSION_COOKIE,
        value=token,
        httponly=True,
        secure=settings.is_production,
        samesite="lax",
        max_age=SESSION_MAX_AGE_SECONDS,
    )
    return response


@router.post("/logout")
async def studio_logout() -> RedirectResponse:
    response = RedirectResponse(url=f"{settings.studio_dashboard_path}/", status_code=303)
    response.delete_cookie(SESSION_COOKIE)
    return response


@router.get("/overview", response_class=HTMLResponse)
async def studio_overview(request: Request, db: AsyncSession = Depends(get_db)) -> HTMLResponse:
    company = await _get_company_from_request(request, db)
    if not company:
        return RedirectResponse(url=f"{settings.studio_dashboard_path}/login")

    res = await db.execute(
        select(Company)
        .options(selectinload(Company.games).selectinload(Game.leaderboards))
        .where(Company.company_id == company.company_id)
    )
    company_full = res.scalar_one()

    return templates.TemplateResponse(
        "studio_overview.html",
        {
            "request": request,
            "base": settings.studio_dashboard_path,
            "company": company_full,
            "games": company_full.games,
        },
    )


@router.post("/games")
async def create_game_from_dashboard(
    request: Request,
    name: str = Form(...),
    db: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    company = await _get_company_from_request(request, db)
    if not company:
        return RedirectResponse(url=f"{settings.studio_dashboard_path}/login", status_code=303)

    trimmed_name = name.strip()
    if not trimmed_name:
        raise HTTPException(status_code=400, detail="Game name is required")

    await create_game(db, company_id=company.company_id, name=trimmed_name)
    return RedirectResponse(url=f"{settings.studio_dashboard_path}/overview", status_code=303)


@router.get("/apps/{game_id}", response_class=HTMLResponse)
async def app_dashboard(
    game_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    leaderboard_id: Optional[str] = Query(default=None),
    date_from: Optional[str] = Query(default=None),
    date_to: Optional[str] = Query(default=None),
    device_id: Optional[str] = Query(default=None),
    preset: Optional[str] = Query(default=None),
) -> HTMLResponse:
    company = await _get_company_from_request(request, db)
    if not company:
        return RedirectResponse(url=f"{settings.studio_dashboard_path}/login")

    res = await db.execute(
        select(Game)
        .options(selectinload(Game.leaderboards))
        .where(Game.game_id == game_id, Game.company_id == company.company_id)
    )
    game = res.scalar_one_or_none()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    leaderboards = game.leaderboards
    leaderboard_pks = [lb.leaderboard_pk for lb in leaderboards]

    # Determine selected leaderboard for the right pane
    selected_leaderboard = None
    if leaderboard_id:
        selected_leaderboard = next((lb for lb in leaderboards if lb.leaderboard_id == leaderboard_id), None)
    if selected_leaderboard is None and leaderboards:
        selected_leaderboard = leaderboards[0]

    # Parse date filters
    date_from_dt = None
    date_to_dt = None
    preset_map = {
        "1h": timedelta(hours=1),
        "6h": timedelta(hours=6),
        "24h": timedelta(hours=24),
        "1w": timedelta(weeks=1),
        "1m": timedelta(days=30),
    }
    if preset and preset in preset_map:
        date_to_dt = datetime.utcnow()
        date_from_dt = date_to_dt - preset_map[preset]
        date_from = date_from_dt.isoformat()
        date_to = date_to_dt.isoformat()
    else:
        try:
            if date_from:
                date_from_dt = datetime.fromisoformat(date_from)
            if date_to:
                date_to_dt = datetime.fromisoformat(date_to)
        except ValueError:
            return templates.TemplateResponse(
                "studio_app.html",
                {
                    "request": request,
                    "base": settings.studio_dashboard_path,
                    "company": company,
                    "game": game,
                    "leaderboards": leaderboards,
                    "error": "Invalid date format. Use ISO format, e.g. 2024-01-01",
                },
                status_code=400,
            )

    score_filters = []
    if date_from_dt:
        score_filters.append(ScoreEvent.submitted_at >= date_from_dt)
    if date_to_dt:
        score_filters.append(ScoreEvent.submitted_at <= date_to_dt)
    if selected_leaderboard:
        score_filters.append(ScoreEvent.leaderboard_pk == selected_leaderboard.leaderboard_pk)

    # Counts
    players_count = (
        await db.execute(select(func.count()).select_from(Player).where(Player.game_id == game.game_id))
    ).scalar_one()

    total_scores = 0
    if score_filters:
        total_scores = (
            await db.execute(
                select(func.count()).select_from(ScoreEvent).where(*score_filters)
            )
        ).scalar_one()
    elif selected_leaderboard:
        total_scores = (
            await db.execute(
                select(func.count())
                .select_from(ScoreEvent)
                .where(ScoreEvent.leaderboard_pk == selected_leaderboard.leaderboard_pk)
            )
        ).scalar_one()

    # Leaderboard summaries
    leaderboard_summaries = []
    for lb in leaderboards:
        player_count = (
            await db.execute(
                select(func.count()).select_from(BestScore).where(BestScore.leaderboard_pk == lb.leaderboard_pk)
            )
        ).scalar_one()

        latest_event = (
            await db.execute(
                select(ScoreEvent)
                .where(ScoreEvent.leaderboard_pk == lb.leaderboard_pk)
                .order_by(ScoreEvent.submitted_at.desc())
                .limit(1)
            )
        ).scalar_one_or_none()

        leaderboard_summaries.append(
            {
                "leaderboard": lb,
                "player_count": player_count,
                "latest": latest_event,
            }
        )

    # Device search
    searched_player = None
    player_scores = []
    if device_id:
        searched_player = (
            await db.execute(
                select(Player).where(Player.game_id == game.game_id, Player.device_id == device_id.strip())
            )
        ).scalar_one_or_none()
        if searched_player:
            player_scores = (
                await db.execute(
                    select(Leaderboard, BestScore)
                    .join(BestScore, BestScore.leaderboard_pk == Leaderboard.leaderboard_pk)
                    .where(
                        Leaderboard.game_id == game.game_id,
                        BestScore.player_xid == searched_player.xid,
                    )
                )
            ).all()

    return templates.TemplateResponse(
        "studio_app.html",
        {
            "request": request,
            "base": settings.studio_dashboard_path,
            "company": company,
            "game": game,
            "players_count": players_count,
            "total_scores": total_scores,
            "leaderboard_summaries": leaderboard_summaries,
            "date_from": date_from,
            "date_to": date_to,
            "device_id": device_id or "",
            "searched_player": searched_player,
            "player_scores": player_scores,
            "selected_leaderboard": selected_leaderboard,
        },
    )
