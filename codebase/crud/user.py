from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from codebase.crud.base import CRUDBase
from codebase.models.user import User
from codebase.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_username(self, db: AsyncSession, *, username: str) -> Optional[User]:
        """Get user by username"""
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        """Get user by email"""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        """Create new user with validation"""
        # Check if username or email already exists
        existing_user = await self.get_by_username(db, username=obj_in.username)
        if existing_user:
            raise ValueError(f"Username '{obj_in.username}' already exists")
        
        existing_email = await self.get_by_email(db, email=obj_in.email)
        if existing_email:
            raise ValueError(f"Email '{obj_in.email}' already exists")
        
        return await super().create(db, obj_in=obj_in)


user = CRUDUser(User)