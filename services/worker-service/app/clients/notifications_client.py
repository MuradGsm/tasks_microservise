import time

import httpx

from app.config import settings
from app.core.logging import get_logger
from app.core.metrics import (
    downstream_http_request_duration_seconds,
    downstream_http_requests_total,
)

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

        duration = time.perf_counter() - started
        duration_ms = round(duration * 1000, 2)

        downstream_http_requests_total.labels(
            target_service="notifications-service",
            method="POST",
            status=str(response.status_code),
        ).inc()
        downstream_http_request_duration_seconds.labels(
            target_service="notifications-service",
            method="POST",
        ).observe(duration)

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

    except httpx.RequestError as exc:
        duration = time.perf_counter() - started
        duration_ms = round(duration * 1000, 2)

        downstream_http_requests_total.labels(
            target_service="notifications-service",
            method="POST",
            status="error",
        ).inc()
        downstream_http_request_duration_seconds.labels(
            target_service="notifications-service",
            method="POST",
        ).observe(duration)

        logger.exception(
            "notifications-service request failed",
            extra={
                "target_service": "notifications-service",
                "url": url,
                "recipient_id": user_id,
                "duration_ms": duration_ms,
                "error": str(exc),
            },
        )
        raise RuntimeError(f"Notifications service unavailable: {exc}")