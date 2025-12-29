from __future__ import annotations

from typing import Any

import httpx

from core.config import get_settings


async def chat_with_coze(messages: list[dict[str, str]], model: str | None, temperature: float | None) -> dict:
    settings = get_settings()
    if not settings.coze_base_url or not settings.coze_api_key:
        return {
            "reply": "Coze Agent 服务未配置，请设置 COZE_BASE_URL 与 COZE_API_KEY。",
            "raw": None,
        }

    payload: dict[str, Any] = {
        "model": model or settings.coze_model,
        "messages": messages,
    }
    if temperature is not None:
        payload["temperature"] = temperature

    headers = {"Authorization": f"Bearer {settings.coze_api_key}"}
    url = settings.coze_base_url.rstrip("/") + "/v1/chat/completions"
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
    reply = (
        data.get("choices", [{}])[0]
        .get("message", {})
        .get("content", "")
    )
    return {"reply": reply, "raw": data}
