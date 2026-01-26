from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from codebase.models import Company


_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return _pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return _pwd_context.verify(password, password_hash)


async def create_company(db: AsyncSession, name: str, login_id: str, password: str) -> Company:
    company = Company(name=name, login_id=login_id, password_hash=hash_password(password))
    db.add(company)
    await db.commit()
    await db.refresh(company)
    return company


async def get_company_by_id(db: AsyncSession, company_id) -> Company | None:
    stmt = select(Company).where(Company.company_id == company_id)
    res = await db.execute(stmt)
    return res.scalar_one_or_none()


async def get_company_by_login(db: AsyncSession, login_id: str) -> Company | None:
    stmt = select(Company).where(Company.login_id == login_id)
    res = await db.execute(stmt)
    return res.scalar_one_or_none()


async def update_company(
    db: AsyncSession,
    company: Company,
    *,
    name: str | None = None,
    login_id: str | None = None,
    password: str | None = None,
) -> Company:
    if name:
        company.name = name
    if login_id:
        company.login_id = login_id
    if password:
        company.password_hash = hash_password(password)
    db.add(company)
    await db.commit()
    await db.refresh(company)
    return company
