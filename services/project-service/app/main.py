from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from prometheus_fastapi_instrumentator import Instrumentator

from app.config.database import get_session
from app.api.v1.router import router as project_router
from app.core.logging import setup_logging, get_logger
from app.middleware.logging import LoggingMiddleware

setup_logging()
logger = get_logger("app.main")

app = FastAPI(title="SJira API Project Service")

app.add_middleware(LoggingMiddleware)
app.include_router(project_router, prefix="/v1")


@app.on_event("startup")
async def startup():
    logger.info("Project service started")


@app.on_event("shutdown")
async def shutdown():
    logger.info("Project service stopped")



@app.get("/health")
async def health():
    return {"status": "ok", "service": "project-service"}


@app.get("/health/db")
async def health_db(session: AsyncSession = Depends(get_session)):
    try:
        await session.execute(text("SELECT 1"))
        return {"status": "ok", "service": "project-service"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"DB error: {e}",
        )


@app.get("/readiness")
async def readiness(session: AsyncSession = Depends(get_session)):
    try:
        await session.execute(text("SELECT 1"))
        return {"status": "ready", "service": "project-service"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Readiness check failed: {e}",
        )

Instrumentator().instrument(app).expose(app)