import asyncio
from typing import Any

from app.clients.notifications_client import push_notification
from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


async def send_notification_with_retry(
    user_id: int,
    payload: dict,
    event_context: dict[str, Any] | None = None,
) -> None:
    attempts = settings.NOTIFICATION_RETRY_ATTEMPTS
    base_delay = settings.NOTIFICATION_RETRY_DELAY_SECONDS
    context = event_context or {}

    last_error: Exception | None = None

    for attempt in range(1, attempts + 1):
        try:
            logger.info(
                "Notification delivery attempt started",
                extra={
                    **context,
                    "recipient_id": user_id,
                    "retry_attempt": attempt,
                    "max_attempts": attempts,
                },
            )

            await push_notification(user_id=user_id, payload=payload)

            logger.info(
                "Notification delivered successfully",
                extra={
                    **context,
                    "recipient_id": user_id,
                    "retry_attempt": attempt,
                    "max_attempts": attempts,
                    "delivery_status": "success",
                },
            )
            return

        except Exception as e:
            last_error = e

            logger.warning(
                "Notification delivery attempt failed",
                extra={
                    **context,
                    "recipient_id": user_id,
                    "retry_attempt": attempt,
                    "max_attempts": attempts,
                    "delivery_status": "retrying" if attempt < attempts else "failed",
                    "error": str(e),
                },
            )

            if attempt < attempts:
                delay = base_delay * attempt
                await asyncio.sleep(delay)

    logger.error(
        "Notification delivery failed after all retry attempts",
        extra={
            **context,
            "recipient_id": user_id,
            "max_attempts": attempts,
            "delivery_status": "failed",
            "error": str(last_error),
        },
    )

    raise RuntimeError(
        f"Notification delivery failed after {attempts} attempts "
        f"for user_id={user_id}: {last_error}"
    )