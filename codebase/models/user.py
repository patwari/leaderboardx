from sqlalchemy import Column, String, DateTime, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from codebase.database import Base
import uuid


class User(Base):
    __tablename__ = "users"
    
    xid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    device_id = Column(String(255), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    scores = relationship("Score", back_populates="user", cascade="all, delete-orphan")
    
    # Constraints and indexes
    __table_args__ = (
        Index('ix_users_device_id', 'device_id'),
        Index('ix_users_xid', 'xid'),
        CheckConstraint(
            "device_id ~ '^[A-Za-z0-9\-]+$'",
            name='check_device_id_format'
        ),
    )
    
    def __repr__(self):
        return f"<User(xid={self.xid}, device_id='{self.device_id}')>"