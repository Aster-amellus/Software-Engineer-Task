from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class PaperOut(BaseModel):
    id: int
    arxiv_id: str
    title: Optional[str]
    authors: list[str] | None
    abstract: Optional[str]
    categories: list[str] | None
    published_at: datetime | None
    pdf_url: Optional[str]
    download_status: str

    class Config:
        orm_mode = True
