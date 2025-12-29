from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class SearchConfig(BaseModel):
    fields: List[str] = Field(default_factory=lambda: ["title", "abstract"])
    sortBy: str = "submittedDate"
    sortOrder: str = "descending"
    start: int = 0
    max_results: int = 50


class RuntimeConfig(BaseModel):
    max_papers: int = 20
    top_k: int = 6
    download_concurrency: int = 5
    retry: int = 3


class ProviderConfig(BaseModel):
    llm: dict = Field(default_factory=lambda: {"name": "mock"})
    embedding: dict = Field(default_factory=lambda: {"name": "mock"})


class ProjectCreate(BaseModel):
    topic: str
    keywords: Optional[list[str]] = None
    search: SearchConfig = Field(default_factory=SearchConfig)
    runtime: RuntimeConfig = Field(default_factory=RuntimeConfig)
    providers: ProviderConfig = Field(default_factory=ProviderConfig)


class ProjectOut(BaseModel):
    id: int
    topic: str
    keywords: Optional[list[str]]
    status: str
    stage: str
    progress: int
    config: dict
    created_at: datetime

    class Config:
        orm_mode = True
