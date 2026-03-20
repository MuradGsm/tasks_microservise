from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from prometheus_fastapi_instrumentator import Instrumentator

from app.config.database import get_session
from app.api.v1.router import router as v1_router
from app.core.logging import setup_logging, get_logger
from app.middleware.request_logging import RequestLoggingMiddleware
from app.events.publisher import check_redis_health

setup_logging()
logger = get_logger(__name__)

app = FastAPI(title="SJira API Issue Service")
logger.info("Issue service application initialized")

app.add_middleware(RequestLoggingMiddleware)

app.include_router(v1_router, prefix="/v1")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "issue-service"}


@app.get("/health/db")
async def health_db(session: AsyncSession = Depends(get_session)):
    try:
        await session.execute(text("SELECT 1"))
        return {"status": "ok", "service": "issue-service", "dependency": "db"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"DB error: {e}",
        )


@app.get("/health/redis")
async def health_redis():
    ok = await check_redis_health()
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Redis error",
        )
    return {"status": "ok", "service": "issue-service", "dependency": "redis"}

@app.get("/readiness")
async def readiness(session: AsyncSession = Depends(get_session)):
    db_ok = True
    redis_ok = True

    try:
        await session.execute(text("SELECT 1"))
    except Exception:
        db_ok = False

    redis_ok = await check_redis_health()

    if not db_ok or not redis_ok:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "not_ready",
                "db": db_ok,
                "redis": redis_ok,
            },
        )

    return {
        "status": "ready",
        "service": "issue-service",
        "db": db_ok,
        "redis": redis_ok,
    }

Instrumentator().instrument(app).expose(app)