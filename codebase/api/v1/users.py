from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from codebase.dependencies import get_database, get_pagination_params, PaginationParams
from codebase.schemas.user import UserCreate, UserResponse, UserListResponse, UserUpdate
from codebase.crud.user import user

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/device", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def get_or_create_user_by_device(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_database)
):
    """Get existing user by device ID or create new one"""
    try:
        user_obj = await user.get_or_create_by_device_id(db, device_id=user_in.device_id)
        return user_obj
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get or create user"
        )


@router.get("/device/{device_id}", response_model=UserResponse)
async def get_user_by_device(
    device_id: str,
    db: AsyncSession = Depends(get_database)
):
    """Get user by device ID"""
    db_user = await user.get_by_device_id(db, device_id=device_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with device ID '{device_id}' not found"
        )
    return db_user


@router.get("/{xid}", response_model=UserResponse)
async def get_user_by_xid(
    xid: UUID,
    db: AsyncSession = Depends(get_database)
):
    """Get user by XID (LeaderboardX internal ID)"""
    db_user = await user.get_by_xid(db, xid=xid)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with XID {xid} not found"
        )
    return db_user


@router.get("/", response_model=UserListResponse)
async def list_users(
    db: AsyncSession = Depends(get_database),
    pagination: PaginationParams = Depends(get_pagination_params)
):
    """List users with pagination"""
    users = await user.get_multi(db, skip=pagination.skip, limit=pagination.limit)
    total = await user.get_count(db)
    
    return UserListResponse(
        users=users,
        total=total,
        page=pagination.page,
        size=pagination.size
    )


@router.put("/{xid}", response_model=UserResponse)
async def update_user_by_xid(
    xid: UUID,
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_database)
):
    """Update user by XID (LeaderboardX internal ID)"""
    db_user = await user.get_by_xid(db, xid=xid)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with XID {xid} not found"
        )
    
    try:
        updated_user = await user.update(db, db_obj=db_user, obj_in=user_update)
        return updated_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )