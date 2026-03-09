import json

from app.config import settings
from app.worker.redis_client import redis_client


async def start_event_consumer():
    queue = settings.EVENTS_QUEUE_NAME

    print(f"Worker started. Listening queue: {queue}")

    while True:
        result = await redis_client.blpop(queue)

        _, payload = result

        event = json.loads(payload)

        print("Received event:", event)