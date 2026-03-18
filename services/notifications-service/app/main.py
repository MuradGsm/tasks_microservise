from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import settings
from app.core.logging import get_logger, setup_logging
from app.middleware.logging import LoggingMiddleware
from app.routes.health import router as health_router
from app.routes.internal import router as internal_router
from app.routes.notifications import router as notifications_router
from app.routes.websocket import router as websocket_router

setup_logging()
logger = get_logger("app.main")

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(LoggingMiddleware)

app.include_router(health_router)
app.include_router(websocket_router)
app.include_router(internal_router)
app.include_router(notifications_router)

Instrumentator().instrument(app).expose(app)


@app.on_event("startup")
async def startup_event() -> None:
    logger.info("Notifications service application startup")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    logger.info("Notifications service application shutdown")