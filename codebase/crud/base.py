from typing import Any, Generic, Type, TypeVar, Optional, Sequence
from pydantic import BaseModel
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from codebase.database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, db: AsyncSession, id: int) -> Optional[ModelType]:
        """Get single record by ID"""
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_multi(
        self, 
        db: AsyncSession, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> Sequence[ModelType]:
        """Get multiple records with pagination"""
        result = await db.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def get_count(self, db: AsyncSession) -> int:
        """Get total count of records"""
        result = await db.execute(select(func.count()).select_from(self.model))
        return result.scalar()

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        """Create new record"""
        obj_data = obj_in.model_dump()
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType | dict[str, Any]
    ) -> ModelType:
        """Update existing record"""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, id: int) -> Optional[ModelType]:
        """Delete record by ID"""
        obj = await self.get(db, id)
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj