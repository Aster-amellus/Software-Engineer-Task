from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship

from db.base import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    topic = Column(String, nullable=False)
    keywords = Column(JSON, nullable=True)
    status = Column(String, default="queued")
    stage = Column(String, default="KEYWORD_EXPAND")
    progress = Column(Integer, default=0)
    config = Column(JSON, default={})
    report_markdown = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    papers = relationship("Paper", back_populates="project", cascade="all, delete-orphan")
    analyses = relationship("Analysis", back_populates="project", cascade="all, delete-orphan")
    exports = relationship("Export", back_populates="project", cascade="all, delete-orphan")
