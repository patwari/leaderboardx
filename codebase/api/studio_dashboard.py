"""Studio HTML dashboard for company login and game management."""

from __future__ import annotations

import hmac
import os
from hashlib import sha256
from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from codebase.config import settings
from codebase.crud.company import get_company
from codebase.crud.game import create_game
from codebase.database import get_db
from codebase.models import Company, Game


router = APIRouter(tags=["studio-dashboard"], include_in_schema=False)

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

SESSION_COOKIE = "studio_session"


def _sign_company_id(company_id: str) -> str:
    digest = hmac.new(settings.secret_key.encode("utf-8"), company_id.encode("utf-8"), sha256).hexdigest()
    return f"{company_id}.{digest}"


def _verify_signature(cookie_value: str) -> Optional[str]:
    if not cookie_value or "." not in cookie_value:
        return None
    company_id, signature = cookie_value.split(".", 1)
    expected = hmac.new(settings.secret_key.encode("utf-8"), company_id.encode("utf-8"), sha256).hexdigest()
    if not hmac.compare_digest(signature, expected):
        return None
    return company_id


async def _get_company_from_request(request: Request, db: AsyncSession) -> Optional[Company]:
    cookie_value = request.cookies.get(SESSION_COOKIE, "")
    company_id = _verify_signature(cookie_value)
    if not company_id:
        return None
    return await get_company(db, company_id)


@router.get("/", response_class=HTMLResponse)
async def studio_root(request: Request, db: AsyncSession = Depends(get_db)) -> HTMLResponse:
    company = await _get_company_from_request(request, db)
    if company:
        return RedirectResponse(url=f"{settings.studio_dashboard_path}/overview")
    return templates.TemplateResponse(
        "studio_login.html",
        {"request": request, "base": settings.studio_dashboard_path},
    )


@router.post("/login", response_class=HTMLResponse)
async def studio_login(
    request: Request,
    company_id: str = Form(...),
    company_secret: str = Form(...),
    db: AsyncSession = Depends(get_db),
) -> HTMLResponse:
    company = await get_company(db, company_id, company_secret)
    if not company:
        return templates.TemplateResponse(
            "studio_login.html",
            {"request": request, "error": "Invalid company credentials", "base": settings.studio_dashboard_path},
            status_code=401,
        )

    response = RedirectResponse(url=f"{settings.studio_dashboard_path}/overview", status_code=303)
    response.set_cookie(
        key=SESSION_COOKIE,
        value=_sign_company_id(str(company.company_id)),
        httponly=True,
        secure=settings.is_production,
        samesite="lax",
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
        return RedirectResponse(url=f"{settings.studio_dashboard_path}/")

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
        return RedirectResponse(url=f"{settings.studio_dashboard_path}/", status_code=303)

    trimmed_name = name.strip()
    if not trimmed_name:
        raise HTTPException(status_code=400, detail="Game name is required")

    await create_game(db, company_id=company.company_id, name=trimmed_name)
    return RedirectResponse(url=f"{settings.studio_dashboard_path}/overview", status_code=303)
