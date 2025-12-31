from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from codebase.crud.base import CRUDBase
from codebase.models.leaderboard import Leaderboard
from codebase.schemas.leaderboard import LeaderboardCreate, LeaderboardUpdate


class CRUDLeaderboard(CRUDBase[Leaderboard, LeaderboardCreate, LeaderboardUpdate]):
    async def get_by_name(self, db: AsyncSession, *, name: str) -> Optional[Leaderboard]:
        """Get leaderboard by name"""
        result = await db.execute(select(Leaderboard).where(Leaderboard.name == name))
        return result.scalar_one_or_none()

    async def get_active(
        self, 
        db: AsyncSession, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> Sequence[Leaderboard]:
        """Get active leaderboards"""
        result = await db.execute(
            select(Leaderboard)
            .where(Leaderboard.is_active == True)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def create(self, db: AsyncSession, *, obj_in: LeaderboardCreate) -> Leaderboard:
        """Create new leaderboard with validation"""
        existing = await self.get_by_name(db, name=obj_in.name)
        if existing:
            raise ValueError(f"Leaderboard with name '{obj_in.name}' already exists")
        
        return await super().create(db, obj_in=obj_in)


leaderboard = CRUDLeaderboard(Leaderboard)