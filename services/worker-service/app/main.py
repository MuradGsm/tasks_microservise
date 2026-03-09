import asyncio
from fastapi import FastAPI

from app.config import settings
from app.routes.health import router as health_router
from app.worker.consumer import start_event_consumer

app = FastAPI(title=settings.APP_NAME)

app.include_router(health_router)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(start_event_consumer())