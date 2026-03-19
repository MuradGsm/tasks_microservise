from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from prometheus_fastapi_instrumentator import Instrumentator

from app.config.database import get_session
from app.api.v1.router import router as v1_router
from app.core.logging import setup_logging, get_logger
from app.middleware.request_logging import RequestLoggingMiddleware

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
        return {"status": "ok", "service": "issue-service DB"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"DB error: {e}",
        )


Instrumentator().instrument(app).expose(app)