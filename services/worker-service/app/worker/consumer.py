import json

from app.config import settings
from app.worker.redis_client import redis_client
from app.worker.router import route_event


async def start_event_consumer() -> None:
    queue = settings.EVENTS_QUEUE_NAME

    print(f"Worker started. Listening queue: {queue}")

    while True:
        try:
            result = await redis_client.blpop(queue)
            _, payload = result

            event = json.loads(payload)

            print("Received event:", event)

            await route_event(event)
        except json.JSONDecodeError as e:
            print(f"Invalid JSON event payload: {e}")
        except Exception as e:
            print(f"Worker error while processing event: {e}")