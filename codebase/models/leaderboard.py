import uuid

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from codebase.database import Base


class Leaderboard(Base):
    """A leaderboard scoped to a single game.

    Public id: leaderboard_id (string). Internally we use leaderboard_pk for joins.
    """

    __tablename__ = "leaderboards"

    leaderboard_pk = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    game_id = Column(UUID(as_uuid=True), ForeignKey("games.game_id", ondelete="CASCADE"), nullable=False, index=True)

    # Public identifier from studio (A-Z, a-z, 0-9, '-') and unique per game
    leaderboard_id = Column(String(64), nullable=False)

    name = Column(String(200), nullable=True)

    # "desc" (higher is better) or "asc" (lower is better)
    sort_order = Column(String(4), nullable=False, default="desc")

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    game = relationship("Game", back_populates="leaderboards")
    best_scores = relationship("BestScore", back_populates="leaderboard", cascade="all, delete-orphan")
    score_events = relationship("ScoreEvent", back_populates="leaderboard", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ux_leaderboards_game_id_leaderboard_id", "game_id", "leaderboard_id", unique=True),
        CheckConstraint("leaderboard_id ~ '^[A-Za-z0-9\\-]+$'", name="check_leaderboard_id_format"),
        CheckConstraint("sort_order IN ('asc','desc')", name="check_sort_order"),
    )

    def __repr__(self) -> str:
        return f"<Leaderboard(game_id={self.game_id}, leaderboard_id={self.leaderboard_id!r})>"
