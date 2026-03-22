from fastapi import Request, Response
from fastapi.responses import JSONResponse
import time
import httpx

from app.clients.upstream import get_http_client
from app.core.logging import get_logger
from app.core.metrics import (
    upstream_request_duration_seconds, 
    upstream_requests_total
)

logger = get_logger("app.services.proxy")


async def proxy_request(
    request: Request,
    upstream_url: str,
    *,
    upstream_service: str,
) -> Response:
    body = await request.body()

    headers = {}
    if request.headers.get("content-type"):
        headers["content-type"] = request.headers["content-type"]

    headers["X-User-Id"] = getattr(request.state, "user_id", "")
    headers["X-Request-Id"] = getattr(request.state, "request_id", "")

    logger.info(
        "Upstream request started",
        extra={
            "path": request.url.path,
            "method": request.method,
            "user_id": int(request.state.user_id) if hasattr(request.state, "user_id") else None,
            "upstream_service": upstream_service,
        },
    )

    upstream_started_at = time.perf_counter()

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            upstream_resp = await client.request(
                method=request.method,
                url=upstream_url,
                params=request.query_params,
                content=body,
                headers=headers,
            )
    except httpx.RequestError:
        upstream_request_duration_seconds.labels(
            service=upstream_service,
            outcome="request_error",
        ).observe(time.perf_counter() - upstream_started_at)

        logger.exception(
            "Upstream request failed",
            extra={
                "path": request.url.path,
                "method": request.method,
                "user_id": int(request.state.user_id) if hasattr(request.state, "user_id") else None,
                "upstream_service": upstream_service,
            },
        )
        upstream_requests_total.labels(
            service=upstream_service,
            status="error",
        ).inc()
        return JSONResponse(
            {"detail": f"{upstream_service} unavailable"},
            status_code=503,
        )

    upstream_request_duration_seconds.labels(
        service=upstream_service,
        outcome=f"http_{upstream_resp.status_code}",
    ).observe(time.perf_counter() - upstream_started_at)

    logger.info(
        "Upstream response received",
        extra={
            "path": request.url.path,
            "method": request.method,
            "user_id": int(request.state.user_id) if hasattr(request.state, "user_id") else None,
            "upstream_service": upstream_service,
            "upstream_status": upstream_resp.status_code,
        },
    )

    upstream_requests_total.labels(
        service=upstream_service,
        status=str(upstream_resp.status_code),
    ).inc()

    response = Response(
        content=upstream_resp.content,
        status_code=upstream_resp.status_code,
        media_type=upstream_resp.headers.get("content-type"),
    )
    response.headers["X-Request-Id"] = getattr(request.state, "request_id", "")
    return response