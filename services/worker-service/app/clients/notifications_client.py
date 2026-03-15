import time

import httpx

from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

NOTIFICATIONS_TIMEOUT = 3.0


async def push_notification(user_id: int, payload: dict) -> None:
    url = f"{settings.NOTIFICATIONS_URL.rstrip('/')}/internal/notifications/push"

    body = {
        "user_id": user_id,
        "payload": payload,
    }

    logger.info(
        "Sending notification to notifications-service",
        extra={
            "target_service": "notifications-service",
            "url": url,
            "recipient_id": user_id,
        },
    )

    started = time.perf_counter()

    try:
        async with httpx.AsyncClient(timeout=NOTIFICATIONS_TIMEOUT) as client:
            response = await client.post(url, json=body)

        duration_ms = round((time.perf_counter() - started) * 1000, 2)

        if response.status_code != 200:
            logger.error(
                "notifications-service returned non-200 response",
                extra={
                    "target_service": "notifications-service",
                    "url": url,
                    "recipient_id": user_id,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                    "error": response.text,
                },
            )
            raise RuntimeError(
                f"Notifications service error: {response.status_code} {response.text}"
            )

        logger.info(
            "notifications-service request completed successfully",
            extra={
                "target_service": "notifications-service",
                "url": url,
                "recipient_id": user_id,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )

    except httpx.RequestError as e:
        duration_ms = round((time.perf_counter() - started) * 1000, 2)

        logger.exception(
            "notifications-service request failed",
            extra={
                "target_service": "notifications-service",
                "url": url,
                "recipient_id": user_id,
                "duration_ms": duration_ms,
                "error": str(e),
            },
        )
        raise RuntimeError(f"Notifications service unavailable: {e}")