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


class Player(Base):
    """A player device registered to a game.

    Public auth for clients: (game_id, device_id) -> xid
    """

    __tablename__ = "players"

    xid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    game_id = Column(UUID(as_uuid=True), ForeignKey("games.game_id", ondelete="CASCADE"), nullable=False, index=True)
    device_id = Column(String(255), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    game = relationship("Game", back_populates="players")
    best_scores = relationship("BestScore", back_populates="player", cascade="all, delete-orphan")
    score_events = relationship("ScoreEvent", back_populates="player", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ux_players_game_id_device_id", "game_id", "device_id", unique=True),
        CheckConstraint("device_id ~ '^[A-Za-z0-9\\-]+$'", name="check_device_id_format"),
    )

    def __repr__(self) -> str:
        return f"<Player(xid={self.xid}, game_id={self.game_id}, device_id={self.device_id!r})>"
