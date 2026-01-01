from typing import Sequence
from decimal import Decimal
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from codebase.crud.base import CRUDBase
from codebase.models.score import Score
from codebase.models.user import User
from codebase.schemas.score import ScoreCreate, ScoreUpdate
from uuid import UUID


class CRUDScore(CRUDBase[Score, ScoreCreate, ScoreUpdate]):
    async def get_leaderboard_scores(
        self,
        db: AsyncSession,
        *,
        leaderboard_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[Score]:
        """Get scores for a leaderboard ordered by value (highest first)"""
        result = await db.execute(
            select(Score)
            .where(Score.leaderboard_id == leaderboard_id)
            .order_by(desc(Score.value), Score.submitted_at)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_user_scores(
        self,
        db: AsyncSession,
        *,
        xid: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[Score]:
        """Get all scores for a user"""
        result = await db.execute(
            select(Score)
            .where(Score.xid == xid)
            .order_by(Score.submitted_at)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_user_leaderboard_rank(
        self,
        db: AsyncSession,
        *,
        leaderboard_id: int,
        user_id: UUID
    ) -> tuple[int | None, Score | None]:
        """Get user's rank and best score in a leaderboard"""
        # Get user's best score in this leaderboard
        user_score_result = await db.execute(
            select(Score)
            .where(Score.user_xid == user_id, Score.leaderboard_id == leaderboard_id)
            .order_by(desc(Score.value), Score.submitted_at)
            .limit(1)
        )
        user_score = user_score_result.scalar_one_or_none()
        
        if not user_score:
            return None, None

        # Count scores better than user's best score
        better_scores_result = await db.execute(
            select(func.count(func.distinct(Score.user_id)))
            .where(
                Score.leaderboard_id == leaderboard_id,
                Score.value > user_score.value
            )
        )
        better_scores_count = better_scores_result.scalar()
        
        rank = better_scores_count + 1
        return rank, user_score

    async def get_user_best_score(
        self,
        db: AsyncSession,
        *,
        xid: UUID,
        leaderboard_id: int
    ) -> Score | None:
        """Get user's best score in a leaderboard"""
        result = await db.execute(
            select(Score)
            .where(Score.xid == xid, Score.leaderboard_id == leaderboard_id)
            .order_by(desc(Score.value), Score.submitted_at)
            .limit(1)
        )
        return result.scalar_one_or_none()


score = CRUDScore(Score)