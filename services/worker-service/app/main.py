import asyncio
from fastapi import FastAPI

from app.config import settings
from app.routes.health import router as health_router
from app.worker.consumer import start_event_consumer
from app.core.logging import get_logger, configure_logging

configure_logging()
logger = get_logger(__name__)


app = FastAPI(title=settings.APP_NAME)

app.include_router(health_router)

@app.on_event("startup")
async def startup_event():
    logger.info("Worker application startup")
    asyncio.create_task(start_event_consumer())

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Worker application shutdown")