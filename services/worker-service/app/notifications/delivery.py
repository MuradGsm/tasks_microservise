import asyncio

from app.clients.notifications_client import push_notification
from app.config import settings
from app.core.logging import get_logger
from app.core.metrics import (
    notification_delivery_attempts_total,
    notification_delivery_failures_total,
    notifications_sent_total,
)

logger = get_logger(__name__)


async def deliver_notification(
    recipients: list[int],
    payload: dict,
    event_type: str,
) -> None:
    for recipient_id in recipients:
        delivered = False

        for attempt in range(1, settings.NOTIFICATION_RETRY_ATTEMPTS + 1):
            notification_delivery_attempts_total.labels(
                event_type=event_type
            ).inc()

            try:
                logger.info(
                    "Notification delivery attempt",
                    extra={
                        "event_type": event_type,
                        "recipient_id": recipient_id,
                        "retry_attempt": attempt,
                        "max_attempts": settings.NOTIFICATION_RETRY_ATTEMPTS,
                        "delivery_status": "attempt",
                    },
                )

                await push_notification(recipient_id, payload)

                notifications_sent_total.labels(event_type=event_type).inc()
                delivered = True

                logger.info(
                    "Notification delivered successfully",
                    extra={
                        "event_type": event_type,
                        "recipient_id": recipient_id,
                        "retry_attempt": attempt,
                        "max_attempts": settings.NOTIFICATION_RETRY_ATTEMPTS,
                        "delivery_status": "success",
                    },
                )
                break

            except Exception as exc:
                notification_delivery_failures_total.labels(
                    event_type=event_type
                ).inc()

                logger.warning(
                    "Notification delivery attempt failed",
                    extra={
                        "event_type": event_type,
                        "recipient_id": recipient_id,
                        "retry_attempt": attempt,
                        "max_attempts": settings.NOTIFICATION_RETRY_ATTEMPTS,
                        "delivery_status": "retry",
                        "error": str(exc),
                    },
                )

                if attempt < settings.NOTIFICATION_RETRY_ATTEMPTS:
                    await asyncio.sleep(settings.NOTIFICATION_RETRY_DELAY_SECONDS)

        if not delivered:
            logger.error(
                "Notification delivery failed after all retries",
                extra={
                    "event_type": event_type,
                    "recipient_id": recipient_id,
                    "max_attempts": settings.NOTIFICATION_RETRY_ATTEMPTS,
                    "delivery_status": "failed",
                },
            )