from fastapi import APIRouter, HTTPException, status

from app.worker.redis_client import ping_redis

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict:
    return {
        "status": "ok",
        "service": "worker-service",
    }


@router.get("/ready")
async def readiness() -> dict:
    try:
        redis_ok = await ping_redis()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "error",
                "service": "worker-service",
                "checks": {
                    "redis": "down",
                },
                "error": str(exc),
            },
        ) from exc

    if not redis_ok:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "error",
                "service": "worker-service",
                "checks": {
                    "redis": "down",
                },
            },
        )

    return {
        "status": "ok",
        "service": "worker-service",
        "checks": {
            "redis": "up",
        },
    }