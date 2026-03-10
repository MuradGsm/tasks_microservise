import json

import redis.asyncio as redis

from app.config.config import setting

redis_client =  redis.from_url(setting.REDIS_URL, decode_responses=True)


async def publish_event(event: dict) -> None:
    payload = json.dumps(event)
    await redis_client.rpush(setting.EVENTS_QUEUE_NAME, payload)