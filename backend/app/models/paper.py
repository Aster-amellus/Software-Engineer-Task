from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from db.base import Base


class Paper(Base):
    __tablename__ = "papers"
    __table_args__ = (UniqueConstraint("project_id", "arxiv_id", name="uq_project_arxiv"),)

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), index=True, nullable=False)
    arxiv_id = Column(String, nullable=False)
    title = Column(String)
    authors = Column(JSON)
    abstract = Column(Text)
    categories = Column(JSON)
    published_at = Column(DateTime)
    updated_at = Column(DateTime)
    pdf_url = Column(String)
    local_path = Column(String)
    download_status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="papers")
    analyses = relationship("Analysis", back_populates="paper", cascade="all, delete-orphan")
