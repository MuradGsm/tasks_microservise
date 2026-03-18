import json
import time

from app.config import settings
from app.core.logging import get_logger
from app.core.logging_utils import build_event_log_context
from app.core.metrics import (
    event_processing_duration_seconds,
    events_consumed_total,
    events_failed_total,
)
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
        event_type = "unknown"
        started = None

        try:
            result = await redis_client.blpop(queue)
            _, raw_payload = result

            event = json.loads(raw_payload)
            event_context = build_event_log_context(event)
            event_type = event.get("event_type", "unknown")

            events_consumed_total.labels(event_type=event_type).inc()

            logger.info(
                "Event received from queue",
                extra={
                    "queue": queue,
                    **event_context,
                },
            )

            started = time.perf_counter()

            await route_event(event)

            duration = time.perf_counter() - started
            event_processing_duration_seconds.labels(
                event_type=event_type
            ).observe(duration)

            logger.info(
                "Event processed successfully",
                extra={
                    "queue": queue,
                    "duration_ms": round(duration * 1000, 2),
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
            events_failed_total.labels(event_type=event_type).inc()

            if started is not None:
                duration = time.perf_counter() - started
                event_processing_duration_seconds.labels(
                    event_type=event_type
                ).observe(duration)

            logger.exception(
                "Worker error while processing event",
                extra={
                    "queue": queue,
                    "error": str(e),
                    **event_context,
                },
            )