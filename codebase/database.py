import asyncio

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from codebase.config import settings


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models"""
    pass


# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db() -> AsyncSession:
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_tables():
    """Create all tables.

    In docker-compose, Postgres can be "ready" in logs but still refuse
    connections for a brief moment. We retry a few times to avoid flaky
    startup failures.
    """

    attempts = 15
    delay_s = 0.5
    last_err: Exception | None = None

    for _ in range(attempts):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            return
        except (ConnectionRefusedError, OSError, OperationalError) as e:
            last_err = e
            await asyncio.sleep(delay_s)
            delay_s = min(delay_s * 1.5, 3.0)

    # If we got here, we never connected.
    assert last_err is not None
    raise last_err


async def check_db_health() -> bool:
    """Check database connectivity"""
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False