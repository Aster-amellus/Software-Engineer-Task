import json
import redis

from core.config import get_settings

_settings = get_settings()

redis_client = None
if _settings.redis_url and not _settings.redis_url.startswith("memory"):
    try:
        redis_client = redis.Redis.from_url(_settings.redis_url)
    except Exception:
        redis_client = None


def publish_project_event(project_id: int, event_type: str, payload: dict):
    if not redis_client:
        return
    message = {
        "type": event_type,
        "project_id": project_id,
        "payload": payload,
    }
    try:
        redis_client.publish(f"ws:project:{project_id}", json.dumps(message))
    except Exception:
        return
