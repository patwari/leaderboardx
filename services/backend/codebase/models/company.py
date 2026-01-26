import uuid

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from codebase.database import Base


class Company(Base):
    """A tenant (indie studio/company) in the SaaS."""

    __tablename__ = "companies"

    company_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Human-friendly display name
    name = Column(String(200), nullable=False)

    # Login identifier set by studio (a-z, 0-9, -)
    login_id = Column(String(64), nullable=False, unique=True, index=True)

    # Password hash for studio login
    password_hash = Column(String(255), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    games = relationship("Game", back_populates="company", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Company(company_id={self.company_id}, login_id={self.login_id!r}, name={self.name!r})>"
