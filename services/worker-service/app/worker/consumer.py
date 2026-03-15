import json

from app.config import settings
from app.core.logging import get_logger
from app.core.logging_utils import build_event_log_context
from app.worker.redis_client import redis_client
from app.worker.router import route_event

logger = get_logger(__name__)


async def start_event_consumer() -> None:
    queue = settings.EVENTS_QUEUE_NAME

    logger.info(
        "Worker consumer started",
        extra={"queue": queue},
    )

    while True:
        raw_payload = None
        event_context = {}

        try:
            result = await redis_client.blpop(queue)
            _, raw_payload = result

            event = json.loads(raw_payload)
            event_context = build_event_log_context(event)

            logger.info(
                "Event received from queue",
                extra={
                    "queue": queue,
                    **event_context,
                },
            )

            await route_event(event)

            logger.info(
                "Event processed successfully",
                extra={
                    "queue": queue,
                    **event_context,
                },
            )

        except json.JSONDecodeError as e:
            logger.error(
                "Invalid JSON event payload",
                extra={
                    "queue": queue,
                    "error": str(e),
                },
            )

        except Exception as e:
            logger.exception(
                "Worker error while processing event",
                extra={
                    "queue": queue,
                    "error": str(e),
                    **event_context,
                },
            )