from fastapi import FastAPI

from app.config import settings
from app.routes.health import router as health_router
from app.routes.websocket import router as websocket_router
from app.routes.internal import router as internal_router
from app.routes.notifications import router as notifications_router

app = FastAPI(title=settings.APP_NAME)

app.include_router(health_router)
app.include_router(websocket_router)
app.include_router(internal_router)
app.include_router(notifications_router)