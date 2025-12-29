import asyncio
import json

import redis.asyncio as aioredis
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from api.deps import get_current_user, oauth2_scheme
from core.config import get_settings

router = APIRouter(prefix="/ws", tags=["ws"])
settings = get_settings()


@router.websocket("/projects/{project_id}")
async def project_ws(websocket: WebSocket, project_id: int):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close()
        return
    # basic token validation
    from core.security import decode_access_token

    if decode_access_token(token) is None:
        await websocket.close()
        return

    await websocket.accept()
    if settings.redis_url.startswith("memory"):
        await websocket.send_json({"type": "info", "payload": "PubSub disabled in current config."})
        await websocket.close()
        return

    redis_conn = aioredis.from_url(settings.redis_url)
    pubsub = redis_conn.pubsub()
    await pubsub.subscribe(f"ws:project:{project_id}")
    try:
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message and message.get("data"):
                payload = message["data"]
                try:
                    decoded = json.loads(payload)
                except Exception:
                    decoded = {"raw": str(payload)}
                await websocket.send_json(decoded)
            await asyncio.sleep(0.2)
    except WebSocketDisconnect:
        await pubsub.unsubscribe(f"ws:project:{project_id}")
        await redis_conn.aclose()
    except Exception:
        await websocket.close()
        await redis_conn.aclose()
