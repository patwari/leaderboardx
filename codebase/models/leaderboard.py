from sqlalchemy import Column, String, DateTime, Integer, Text, Boolean, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from codebase.database import Base


class Leaderboard(Base):
    __tablename__ = "leaderboards"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True, nullable=False)
    settings = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    scores = relationship("Score", back_populates="leaderboard", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Leaderboard(id={self.id}, name='{self.name}')>"