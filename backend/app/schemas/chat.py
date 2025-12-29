from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    model: str | None = None
    temperature: float | None = Field(default=0.2, ge=0.0, le=1.0)


class ChatResponse(BaseModel):
    reply: str
    raw: dict | None = None
