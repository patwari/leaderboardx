import secrets
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from codebase.models import Company


def _new_secret() -> str:
    # URL-safe secret, ~43 chars
    return secrets.token_urlsafe(32)


async def create_company(db: AsyncSession, name: str) -> Company:
    company = Company(name=name, company_secret=_new_secret())
    db.add(company)
    await db.commit()
    await db.refresh(company)
    return company


async def get_company(db: AsyncSession, company_id, company_secret: str | None = None) -> Company | None:
    stmt = select(Company).where(Company.company_id == company_id)
    if company_secret is not None:
        stmt = stmt.where(Company.company_secret == company_secret)
    res = await db.execute(stmt)
    return res.scalar_one_or_none()


async def update_company(db: AsyncSession, company: Company, *, name: str | None = None, rotate_secret: bool = False) -> Company:
    if name:
        company.name = name
    if rotate_secret:
        company.company_secret = _new_secret()
    db.add(company)
    await db.commit()
    await db.refresh(company)
    return company
