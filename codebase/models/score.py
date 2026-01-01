from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from codebase.database import Base


class BestScore(Base):
    """Best score for a player on a leaderboard."""

    __tablename__ = "player_leaderboard_best"

    leaderboard_pk = Column(UUID(as_uuid=True), ForeignKey("leaderboards.leaderboard_pk", ondelete="CASCADE"), primary_key=True)
    player_xid = Column(UUID(as_uuid=True), ForeignKey("players.xid", ondelete="CASCADE"), primary_key=True)

    best_value = Column(Integer, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    leaderboard = relationship("Leaderboard", back_populates="best_scores")
    player = relationship("Player", back_populates="best_scores")

    __table_args__ = (
        Index("ix_best_scores_leaderboard", "leaderboard_pk"),
        Index("ix_best_scores_player", "player_xid"),
    )


class ScoreEvent(Base):
    """Append-only score submission history (for studio dashboard analytics)."""

    __tablename__ = "score_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    leaderboard_pk = Column(UUID(as_uuid=True), ForeignKey("leaderboards.leaderboard_pk", ondelete="CASCADE"), nullable=False, index=True)
    player_xid = Column(UUID(as_uuid=True), ForeignKey("players.xid", ondelete="CASCADE"), nullable=False, index=True)
    value = Column(Integer, nullable=False)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    leaderboard = relationship("Leaderboard", back_populates="score_events")
    player = relationship("Player", back_populates="score_events")

    __table_args__ = (
        Index("ix_score_events_leaderboard_time", "leaderboard_pk", "submitted_at"),
        Index("ix_score_events_player_time", "player_xid", "submitted_at"),
    )
