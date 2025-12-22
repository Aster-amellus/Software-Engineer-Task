import json
import redis

from core.config import get_settings

_settings = get_settings()
redis_client = redis.Redis.from_url(_settings.redis_url)


def publish_project_event(project_id: int, event_type: str, payload: dict):
    message = {
        "type": event_type,
        "project_id": project_id,
        "payload": payload,
    }
    redis_client.publish(f"ws:project:{project_id}", json.dumps(message))
