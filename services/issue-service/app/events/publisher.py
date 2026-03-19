import json

import redis.asyncio as redis

from app.config.config import setting
from app.core.logging import get_logger
from app.core.metrics import issue_events_published_total, issue_events_publish_failed_total

logger = get_logger(__name__)

redis_client =  redis.from_url(setting.REDIS_URL, decode_responses=True)


async def publish_event(event: dict) -> None:
    payload = json.dumps(event)
    event_type = event.get("event_type", "unkown")


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
        issue_events_published_total.labels(event_type=event_type).inc()

        logger.info(
            "Event published to Redis queue",
            extra={
                "event_type": event.get("event_type"),
                "issue_id": event.get("issue_id"),
                "project_id": event.get("project_id"),
            },
        )
    except Exception:
        issue_events_publish_failed_total.labels(event_type=event_type).inc()

        logger.exception(
            "Failed to publish event to Redis queue",
            extra={
                "event_type": event.get("event_type"),
                "issue_id": event.get("issue_id"),
                "project_id": event.get("project_id"),
            },
        )
        raise