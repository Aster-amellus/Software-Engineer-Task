from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship

from db.base import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), index=True, nullable=False)
    paper_id = Column(Integer, ForeignKey("papers.id"), index=True, nullable=False)
    schema_version = Column(String, default="v1")
    extracted = Column(JSON)
    summary = Column(Text)
    token_cost = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="analyses")
    paper = relationship("Paper", back_populates="analyses")
