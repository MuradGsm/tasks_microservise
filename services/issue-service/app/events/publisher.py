import json

import redis.asyncio as redis

from app.config.config import setting
from app.core.logging import get_logger

logger = get_logger(__name__)

redis_client =  redis.from_url(setting.REDIS_URL, decode_responses=True)


async def publish_event(event: dict) -> None:
    payload = json.dumps(event)

    logger.info(
        "Publishing event to Redis queue",
        extra={
            "event_type": event.get("event_type"),
            "issue_id": event.get("issue_id"),
            "project_id": event.get("project_id"),
        },
    )

    try:
        await redis_client.rpush(setting.EVENTS_QUEUE_NAME, payload)

        logger.info(
            "Event published to Redis queue",
            extra={
                "event_type": event.get("event_type"),
                "issue_id": event.get("issue_id"),
                "project_id": event.get("project_id"),
            },
        )
    except Exception:
        logger.exception(
            "Failed to publish event to Redis queue",
            extra={
                "event_type": event.get("event_type"),
                "issue_id": event.get("issue_id"),
                "project_id": event.get("project_id"),
            },
        )
        raise