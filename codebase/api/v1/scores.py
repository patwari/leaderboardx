from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from codebase.dependencies import get_database
from codebase.schemas.score import ScoreCreate, ScoreResponse
from decimal import Decimal
from codebase.crud.score import score
from codebase.crud.user import user
from codebase.crud.leaderboard import leaderboard

router = APIRouter(
    prefix="/scores",
    tags=["scores"]
)

@router.post("/leaderboards/{leaderboard_id}/scores", response_model=ScoreResponse, status_code=status.HTTP_201_CREATED)
async def submit_score(
    leaderboard_id: int,
    user_id: int,
    score_value: float,
    db: AsyncSession = Depends(get_database)
):
    """Submit a score to a leaderboard"""
    # Validate leaderboard exists
    db_leaderboard = await leaderboard.get(db, id=leaderboard_id)
    if not db_leaderboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leaderboard not found"
        )

    # Validate user exists
    db_user = await user.get(db, id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Create score
    score_create = ScoreCreate(
        user_id=user_id,
        leaderboard_id=leaderboard_id,
        value=Decimal(str(score_value))
    )

    try:
        created_score = await score.create(db, obj_in=score_create)
        return created_score
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while submitting the score"
        )
