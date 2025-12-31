from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from codebase.dependencies import get_database
from codebase.schemas.leaderboard import LeaderboardCreate, LeaderboardResponse
from codebase.crud.leaderboard import leaderboard

router = APIRouter(prefix="/leaderboards", tags=["leaderboards"])


@router.post("/", response_model=LeaderboardResponse, status_code=status.HTTP_201_CREATED)
async def create_leaderboard(
    leaderboard_in: LeaderboardCreate,
    db: AsyncSession = Depends(get_database)
):
    """Create a new leaderboard"""
    try:
        created_leaderboard = await leaderboard.create(db, obj_in=leaderboard_in)
        return created_leaderboard
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create leaderboard"
        )