import uuid

import httpx
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.clients.identity import check_identity_health
from app.clients.upstream import get_http_client
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger("app.routes.health")


@router.get("/health")
async def health():
    return {"status": "ok", "service": "api-gateway"}


@router.get("/ready")
async def ready():
    checks: dict[str, str] = {}

    try:
        get_http_client()
        checks["http_client"] = "ok"
    except RuntimeError:
        checks["http_client"] = "fail"
        logger.error("Readiness failed: HTTP client is not initialized")
        return JSONResponse(
            {
                "status": "fail",
                "service": "api-gateway",
                "checks": checks,
            },
            status_code=503,
        )

    request_id = str(uuid.uuid4())

    try:
        identity_resp = await check_identity_health(request_id)
    except httpx.RequestError:
        checks["identity_service"] = "fail"
        logger.exception(
            "Readiness failed: identity-service unavailable",
            extra={"upstream_service": "identity-service"},
        )
        return JSONResponse(
            {
                "status": "fail",
                "service": "api-gateway",
                "checks": checks,
            },
            status_code=503,
        )

    if identity_resp.status_code != 200:
        checks["identity_service"] = "fail"
        logger.warning(
            "Readiness failed: identity-service unhealthy",
            extra={
                "upstream_service": "identity-service",
                "upstream_status": identity_resp.status_code,
            },
        )
        return JSONResponse(
            {
                "status": "fail",
                "service": "api-gateway",
                "checks": checks,
            },
            status_code=503,
        )

    checks["identity_service"] = "ok"

    return {
        "status": "ok",
        "service": "api-gateway",
        "checks": checks,
    }