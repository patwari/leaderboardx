from sqlalchemy import Column, Integer, DateTime, ForeignKey, Numeric, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from codebase.database import Base


class Score(Base):
    __tablename__ = "scores"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    leaderboard_id = Column(Integer, ForeignKey("leaderboards.id"), nullable=False)
    value = Column(Numeric(20, 4), nullable=False)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="scores")
    leaderboard = relationship("Leaderboard", back_populates="scores")
    
    # Composite indexes for performance
    __table_args__ = (
        Index('ix_scores_leaderboard_value', 'leaderboard_id', 'value'),
        Index('ix_scores_user_leaderboard', 'user_id', 'leaderboard_id'),
    )
    
    def __repr__(self):
        return f"<Score(id={self.id}, user_id={self.user_id}, value={self.value})>"