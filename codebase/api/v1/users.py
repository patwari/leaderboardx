from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from codebase.dependencies import get_database, get_pagination_params, PaginationParams
from codebase.schemas.user import UserCreate, UserResponse, UserListResponse, UserUpdate
from codebase.crud.user import user

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_database)
):
    """Create a new user"""
    try:
        created_user = await user.create(db, obj_in=user_in)
        return created_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_database)
):
    """Get user by ID"""
    db_user = await user.get(db, id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
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


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_database)
):
    """Update user by ID"""
    db_user = await user.get(db, id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
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