from datetime import datetime
from pydantic import BaseModel


class ExportOut(BaseModel):
    id: int
    format: str
    local_path: str
    status: str
    created_at: datetime

    class Config:
        orm_mode = True
