import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from codebase.database import Base


class Game(Base):
    """A game registered under a company."""

    __tablename__ = "games"

    game_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.company_id", ondelete="CASCADE"), nullable=False, index=True)

    name = Column(String(200), nullable=False)

    # Optional secret for studio server-side calls for this specific game
    game_secret = Column(String(64), nullable=False, unique=True, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    company = relationship("Company", back_populates="games")
    leaderboards = relationship("Leaderboard", back_populates="game", cascade="all, delete-orphan")
    players = relationship("Player", back_populates="game", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_games_company_id_name", "company_id", "name"),
    )

    def __repr__(self) -> str:
        return f"<Game(game_id={self.game_id}, name={self.name!r})>"
