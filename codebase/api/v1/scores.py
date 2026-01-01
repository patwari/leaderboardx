from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from codebase.dependencies import get_database
from codebase.schemas.score import ScoreCreate, ScoreResponse, ScoreListResponse
from codebase.dependencies import get_pagination_params, PaginationParams
from decimal import Decimal
from codebase.crud.score import score
from codebase.crud.user import user
from codebase.crud.leaderboard import leaderboard
from sqlalchemy import select, func
from codebase.models.score import Score
import logging
from uuid import UUID

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/scores",
    tags=["scores"]
)

@router.post("/leaderboards/{leaderboard_id}/scores", response_model=ScoreResponse, status_code=status.HTTP_201_CREATED)
async def submit_score(
    leaderboard_id: int,
    device_id: str,
    score_value: float,
    db: AsyncSession = Depends(get_database)
):
    """Submit a score to a leaderboard"""
    # Validate leaderboard exists and is active
    db_leaderboard = await leaderboard.get(db, id=leaderboard_id)
    if not db_leaderboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leaderboard not found"
        )

    if not db_leaderboard.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Leaderboard is not active"
        )

    # Validate user exists
    db_user = await user.get_by_device_id(db, device_id=device_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Validate score value
    if score_value < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Score value must be non-negative"
        )

    if score_value > 999999999:  # Reasonable upper limit
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Score value exceeds the maximum allowed limit"
        )

    # Create score
    score_create = ScoreCreate(
        xid=db_user.xid,
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

@router.get("/leaderboards/{leaderboard_id}/scores", response_model=ScoreListResponse)
async def get_leaderboard_scores(
    leaderboard_id: int,
    db: AsyncSession = Depends(get_database),
    pagination: PaginationParams = Depends(get_pagination_params)
):
    """Get scores for a leaderboard (ranking)"""
    logger.info(f"Fetching leaderboard with ID: {leaderboard_id}")
    db_leaderboard = await leaderboard.get(db, id=leaderboard_id)
    if not db_leaderboard:
        logger.warning(f"Leaderboard with ID {leaderboard_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leaderboard not found"
        )

    logger.info(f"Leaderboard found: {db_leaderboard}")

    # Fetch scores with ranking
    logger.info(f"Fetching scores for leaderboard ID: {leaderboard_id}")
    scores = await score.get_leaderboard_scores(
        db,
        leaderboard_id=leaderboard_id,
        skip=pagination.skip,
        limit=pagination.limit
    )
    logger.info(f"Scores fetched: {scores}")

    # Get total count for this leaderboard
    logger.info(f"Fetching total score count for leaderboard ID: {leaderboard_id}")
    total_result = await db.execute(
        select(func.count()).select_from(Score).where(Score.leaderboard_id == leaderboard_id)
    )
    total = total_result.scalar()
    logger.info(f"Total scores count: {total}")

    return ScoreListResponse(
        scores=scores,
        total=total,
        page=pagination.page,
        size=pagination.size
    )

@router.get("/users/{user_id}/scores", response_model=ScoreListResponse)
async def get_user_scores(
    user_id: UUID,
    db: AsyncSession = Depends(get_database),
    pagination: PaginationParams = Depends(get_pagination_params)
):
    """Get all scores for a user"""
    # Validate user exists
    db_user = await user.get(db, id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Fetch scores for the user
    scores = await score.get_user_scores(
        db,
        user_id=user_id,
        skip=pagination.skip,
        limit=pagination.limit
    )

    # Get total count for this user
    total_result = await db.execute(
        select(func.count()).select_from(Score).where(Score.user_xid == user_id)
    )
    total = total_result.scalar()

    return ScoreListResponse(
        scores=scores,
        total=total,
        page=pagination.page,
        size=pagination.size
    )

@router.get("/leaderboards/{leaderboard_id}/devices/{device_id}/rank")
async def get_device_rank(
    leaderboard_id: int,
    device_id: str,
    db: AsyncSession = Depends(get_database)
):
    """Get device's rank in a leaderboard"""
    # Validate leaderboard exists
    db_leaderboard = await leaderboard.get(db, id=leaderboard_id)
    if not db_leaderboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leaderboard not found"
        )

    # Map device_id to xid
    db_user = await user.get_by_device_id(db, device_id=device_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )

    # Retrieve user rank and score
    rank, user_score = await score.get_user_leaderboard_rank(
        db,
        leaderboard_id=leaderboard_id,
        user_id=db_user.xid
    )

    if rank is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device has no score in this leaderboard"
        )

    return {
        "device_id": device_id,
        "rank": rank,
        "score": user_score.value,
        "submitted_at": user_score.submitted_at
    }
