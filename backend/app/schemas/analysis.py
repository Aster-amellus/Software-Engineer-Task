from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AnalysisOut(BaseModel):
    id: int
    paper_id: int
    schema_version: str
    extracted: dict | None
    summary: Optional[str]
    token_cost: Optional[int]
    created_at: datetime

    class Config:
        orm_mode = True
