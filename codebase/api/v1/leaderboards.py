from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from codebase.dependencies import get_database, get_pagination_params, PaginationParams
from codebase.schemas.leaderboard import LeaderboardCreate, LeaderboardResponse, LeaderboardListResponse, LeaderboardUpdate
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


@router.get("/{leaderboard_id}", response_model=LeaderboardResponse)
async def get_leaderboard(
    leaderboard_id: int,
    db: AsyncSession = Depends(get_database)
):
    """Get leaderboard by ID"""
    db_leaderboard = await leaderboard.get(db, id=leaderboard_id)
    if not db_leaderboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Leaderboard with ID {leaderboard_id} not found"
        )
    return db_leaderboard


@router.get("/", response_model=LeaderboardListResponse)
async def list_leaderboards(
    active_only: bool = False,
    db: AsyncSession = Depends(get_database),
    pagination: PaginationParams = Depends(get_pagination_params)
):
    """List leaderboards with pagination"""
    if active_only:
        leaderboards = await leaderboard.get_active(db, skip=pagination.skip, limit=pagination.limit)
    else:
        leaderboards = await leaderboard.get_multi(db, skip=pagination.skip, limit=pagination.limit)
    
    total = await leaderboard.get_count(db)
    
    return LeaderboardListResponse(
        leaderboards=leaderboards,
        total=total,
        page=pagination.page,
        size=pagination.size
    )


@router.put("/{leaderboard_id}", response_model=LeaderboardResponse)
async def update_leaderboard(
    leaderboard_id: int,
    leaderboard_update: LeaderboardUpdate,
    db: AsyncSession = Depends(get_database)
):
    """Update leaderboard by ID"""
    db_leaderboard = await leaderboard.get(db, id=leaderboard_id)
    if not db_leaderboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Leaderboard with ID {leaderboard_id} not found"
        )
    
    try:
        updated_leaderboard = await leaderboard.update(db, db_obj=db_leaderboard, obj_in=leaderboard_update)
        return updated_leaderboard
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update leaderboard"
        )