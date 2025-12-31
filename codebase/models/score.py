from sqlalchemy import Column, Integer, DateTime, ForeignKey, Numeric, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from codebase.database import Base
import uuid


class Score(Base):
    __tablename__ = "scores"
    
    xid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_xid = Column(UUID(as_uuid=True), ForeignKey("users.xid"), nullable=False)
    leaderboard_id = Column(Integer, ForeignKey("leaderboards.id"), nullable=False)
    value = Column(Numeric(20, 4), nullable=False)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="scores")
    leaderboard = relationship("Leaderboard", back_populates="scores")
    
    # Composite indexes for performance
    __table_args__ = (
        Index('ix_scores_leaderboard_value', 'leaderboard_id', 'value'),
        Index('ix_scores_user_leaderboard', 'user_xid', 'leaderboard_id'),
        Index('ix_scores_xid', 'xid'),
    )
    
    def __repr__(self):
        return f"<Score(xid={self.xid}, user_xid={self.user_xid}, value={self.value})>"