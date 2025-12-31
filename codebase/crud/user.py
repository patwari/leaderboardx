from typing import Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from codebase.crud.base import CRUDBase
from codebase.models.user import User
from codebase.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_device_id(self, db: AsyncSession, *, device_id: str) -> Optional[User]:
        """Get user by device ID"""
        result = await db.execute(select(User).where(User.device_id == device_id))
        return result.scalar_one_or_none()

    async def get_by_xid(self, db: AsyncSession, *, xid: UUID) -> Optional[User]:
        """Get user by xid (internal LeaderboardX ID)"""
        result = await db.execute(select(User).where(User.xid == xid))
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        """Create new user with device ID"""
        # Check if device_id already exists
        existing_user = await self.get_by_device_id(db, device_id=obj_in.device_id)
        if existing_user:
            raise ValueError(f"Device ID '{obj_in.device_id}' already exists")
        
        return await super().create(db, obj_in=obj_in)

    async def get_or_create_by_device_id(self, db: AsyncSession, *, device_id: str) -> User:
        """Get user by device ID, create if doesn't exist"""
        existing_user = await self.get_by_device_id(db, device_id=device_id)
        if existing_user:
            return existing_user
        
        # Create new user with device_id
        user_create = UserCreate(device_id=device_id)
        return await self.create(db, obj_in=user_create)


user = CRUDUser(User)