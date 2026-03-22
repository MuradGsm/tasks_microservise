import time

import httpx

from app.config import settings
from app.core.logging import get_logger
from app.core.metrics import (
    downstream_http_request_duration_seconds,
    downstream_http_requests_total,
)

logger = get_logger(__name__)

ISSUE_TIMEOUT = 3.0


async def get_issue(issue_id: int) -> dict:
    url = f"{settings.ISSUE_URL.rstrip('/')}/internal/issues/{issue_id}"

    logger.info(
        "Requesting issue from issue-service",
        extra={
            "target_service": "issue-service",
            "url": url,
            "issue_id": issue_id,
        },
    )

    started = time.perf_counter()

    try:
        async with httpx.AsyncClient(timeout=ISSUE_TIMEOUT) as client:
            response = await client.get(url)

        duration = time.perf_counter() - started
        duration_ms = round(duration * 1000, 2)

        downstream_http_requests_total.labels(
            target_service="issue-service",
            method="GET",
            status=str(response.status_code),
        ).inc()
        downstream_http_request_duration_seconds.labels(
            target_service="issue-service",
            method="GET",
        ).observe(duration)

        if response.status_code != 200:
            logger.error(
                "issue-service returned non-200 response",
                extra={
                    "target_service": "issue-service",
                    "url": url,
                    "issue_id": issue_id,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                    "error": response.text,
                },
            )
            raise RuntimeError(
                f"Issue service error: {response.status_code} {response.text}"
            )

        logger.info(
            "issue-service request completed successfully",
            extra={
                "target_service": "issue-service",
                "url": url,
                "issue_id": issue_id,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )
        return response.json()

    except httpx.RequestError as exc:
        duration = time.perf_counter() - started
        duration_ms = round(duration * 1000, 2)

        downstream_http_requests_total.labels(
            target_service="issue-service",
            method="GET",
            status="error",
        ).inc()
        downstream_http_request_duration_seconds.labels(
            target_service="issue-service",
            method="GET",
        ).observe(duration)

        logger.exception(
            "issue-service request failed",
            extra={
                "target_service": "issue-service",
                "url": url,
                "issue_id": issue_id,
                "duration_ms": duration_ms,
                "error": str(exc),
            },
        )
        raise RuntimeError(f"Issue service unavailable: {exc}")