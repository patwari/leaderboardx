"""Admin HTML dashboard (developer/operator view).

This is intentionally simple (server-rendered HTML) so you can monitor:
- process/system memory
- counts (companies/games/leaderboards/players/events)
- browse company -> game -> leaderboard states

Auth: for now, a single shared token (ADMIN_TOKEN). Send it as:
- header: X-Admin-Token: <token>
- OR query param: ?token=<token>

In development, if ADMIN_TOKEN is empty, auth is skipped.
"""

from __future__ import annotations

import os
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from codebase.config import settings
from codebase.database import get_db
from codebase.models.company import Company
from codebase.models.game import Game
from codebase.models.leaderboard import Leaderboard
from codebase.models.player import Player
from codebase.models.score import BestScore
from codebase.models.score import ScoreEvent


router = APIRouter(tags=["admin-dashboard"], include_in_schema=False)

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


def _require_admin(request: Request) -> None:
    """Simple shared-token protection for the admin dashboard."""

    # In dev, allow if token not configured.
    if settings.is_development and not settings.admin_token:
        return

    token: Optional[str] = request.headers.get("X-Admin-Token")
    if not token:
        token = request.query_params.get("token")

    if not token or token != settings.admin_token:
        raise HTTPException(status_code=401, detail="Unauthorized")


async def _counts(db: AsyncSession) -> dict:
    res = {}
    res["companies"] = (await db.execute(select(func.count()).select_from(Company))).scalar_one()
    res["games"] = (await db.execute(select(func.count()).select_from(Game))).scalar_one()
    res["leaderboards"] = (await db.execute(select(func.count()).select_from(Leaderboard))).scalar_one()
    res["players"] = (await db.execute(select(func.count()).select_from(Player))).scalar_one()
    res["score_events"] = (await db.execute(select(func.count()).select_from(ScoreEvent))).scalar_one()
    res["best_scores"] = (await db.execute(select(func.count()).select_from(BestScore))).scalar_one()
    return res


def _memory_snapshot() -> dict:
    """Return basic process + system memory stats without external dependencies.

    This works well inside Linux containers by reading from /proc.
    """

    def _read_kb_from_file(filepath: str, key: str):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith(key):
                        parts = line.split()
                        # e.g. "VmRSS:  12345 kB" or "MemTotal:  16384256 kB"
                        if len(parts) >= 2 and parts[1].isdigit():
                            return int(parts[1])
        except FileNotFoundError:
            return None
        return None

    # Process RSS from /proc/self/status (kB)
    rss_kb = _read_kb_from_file("/proc/self/status", "VmRSS:")
    process_rss_bytes = int(rss_kb * 1024) if rss_kb is not None else 0

    # System memory from /proc/meminfo (kB)
    total_kb = _read_kb_from_file("/proc/meminfo", "MemTotal:")
    avail_kb = _read_kb_from_file("/proc/meminfo", "MemAvailable:")

    system_total_bytes = int(total_kb * 1024) if total_kb is not None else 0
    system_available_bytes = int(avail_kb * 1024) if avail_kb is not None else 0
    system_used_bytes = max(system_total_bytes - system_available_bytes, 0)

    system_percent = float((system_used_bytes / system_total_bytes) * 100.0) if system_total_bytes else 0.0

    return {
        "process_rss_bytes": process_rss_bytes,
        "system_total_bytes": system_total_bytes,
        "system_used_bytes": system_used_bytes,
        "system_available_bytes": system_available_bytes,
        "system_percent": system_percent,
    }


@router.get("/", response_class=HTMLResponse)
async def dashboard_root(request: Request) -> RedirectResponse:
    _require_admin(request)
    return RedirectResponse(url=f"{settings.admin_dashboard_path}/overview")


@router.get("/overview", response_class=HTMLResponse)
async def overview(request: Request, db: AsyncSession = Depends(get_db)) -> HTMLResponse:
    _require_admin(request)

    counts = await _counts(db)
    mem = _memory_snapshot()

    # Latest events (for quick sanity)
    latest_events = (
        await db.execute(
            select(ScoreEvent)
            .order_by(ScoreEvent.submitted_at.desc())
            .limit(25)
        )
    ).scalars().all()

    return templates.TemplateResponse(
        "admin_overview.html",
        {
            "request": request,
            "base": settings.admin_dashboard_path,
            "counts": counts,
            "mem": mem,
            "latest_events": latest_events,
        },
    )


@router.get("/companies", response_class=HTMLResponse)
async def companies(request: Request, db: AsyncSession = Depends(get_db)) -> HTMLResponse:
    _require_admin(request)

    items = (
        await db.execute(
            select(Company).order_by(Company.created_at.desc()).limit(500)
        )
    ).scalars().all()

    return templates.TemplateResponse(
        "admin_companies.html",
        {"request": request, "base": settings.admin_dashboard_path, "companies": items},
    )


@router.get("/companies/{company_id}", response_class=HTMLResponse)
async def company_detail(company_id: str, request: Request, db: AsyncSession = Depends(get_db)) -> HTMLResponse:
    _require_admin(request)

    company = (await db.execute(select(Company).where(Company.company_id == company_id))).scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    games = (
        await db.execute(select(Game).where(Game.company_id == company.company_id).order_by(Game.created_at.desc()))
    ).scalars().all()

    return templates.TemplateResponse(
        "admin_company_detail.html",
        {"request": request, "base": settings.admin_dashboard_path, "company": company, "games": games},
    )


@router.get("/games/{game_id}", response_class=HTMLResponse)
async def game_detail(game_id: str, request: Request, db: AsyncSession = Depends(get_db)) -> HTMLResponse:
    _require_admin(request)

    game = (await db.execute(select(Game).where(Game.game_id == game_id))).scalar_one_or_none()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    company = (await db.execute(select(Company).where(Company.company_id == game.company_id))).scalar_one_or_none()

    lbs = (
        await db.execute(select(Leaderboard).where(Leaderboard.game_id == game.game_id).order_by(Leaderboard.created_at.desc()))
    ).scalars().all()

    # For each leaderboard, pull top 25 best scores
    leaderboard_states = []
    for lb in lbs:
        top = (
            await db.execute(
                select(BestScore)
                .where(BestScore.leaderboard_pk == lb.leaderboard_pk)
                .order_by(BestScore.best_value.desc() if lb.sort_order == "desc" else BestScore.best_value.asc())
                .limit(25)
            )
        ).scalars().all()
        leaderboard_states.append({"lb": lb, "top": top})

    # Player count for this game
    players_count = (
        await db.execute(select(func.count()).select_from(Player).where(Player.game_id == game.game_id))
    ).scalar_one()

    return templates.TemplateResponse(
        "admin_game_detail.html",
        {
            "request": request,
            "base": settings.admin_dashboard_path,
            "company": company,
            "game": game,
            "players_count": players_count,
            "leaderboard_states": leaderboard_states,
        },
    )
