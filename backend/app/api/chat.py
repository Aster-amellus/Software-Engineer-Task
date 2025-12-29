from fastapi import APIRouter, Depends, HTTPException

from api.deps import get_current_user
from schemas.chat import ChatRequest, ChatResponse
from services.coze import chat_with_coze

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, _user=Depends(get_current_user)):
    try:
        payload = await chat_with_coze(
            [message.dict() for message in req.messages],
            req.model,
            req.temperature,
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return ChatResponse(**payload)
