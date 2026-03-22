import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import settings
from app.core.logging import configure_logging, get_logger
from app.routes.health import router as health_router
from app.worker.consumer import start_event_consumer
from app.worker.redis_client import close_redis

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Worker application startup")

    consumer_task = asyncio.create_task(start_event_consumer())
    app.state.consumer_task = consumer_task

    try:
        yield
    finally:
        logger.info("Worker application shutdown started")

        consumer_task.cancel()
        try:
            await consumer_task
        except asyncio.CancelledError:
            logger.info("Worker consumer task cancelled successfully")

        await close_redis()
        logger.info("Worker application shutdown completed")


app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan,
)

app.include_router(health_router)

Instrumentator().instrument(app).expose(app)