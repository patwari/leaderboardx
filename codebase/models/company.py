import uuid

from sqlalchemy import Column, DateTime, String
from sqlalchemy import CheckConstraint
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

    # Dashboard auth
    username = Column(String(50), nullable=False, unique=True, index=True)
    password_hash = Column(String(256), nullable=False)

    # Simple shared secret for server-side studio APIs (dashboard auth comes later)
    company_secret = Column(String(64), nullable=False, unique=True, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    games = relationship("Game", back_populates="company", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("username ~ '^[a-z0-9\\-]+$'", name="check_company_username_format"),
    )

    def __repr__(self) -> str:
        return f"<Company(company_id={self.company_id}, name={self.name!r})>"
