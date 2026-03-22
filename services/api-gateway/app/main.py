from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.clients.upstream import shutdown_http_client, startup_http_client
from app.config import settings
from app.core.logging import get_logger, setup_logging
from app.middleware.auth import register_middlewares
from app.routes.debug import router as debug_router
from app.routes.health import router as health_router
from app.routes.proxy import router as proxy_router

setup_logging()
logger = get_logger("app.main")

app = FastAPI(title="SJira API Gateway")

Instrumentator().instrument(app).expose(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_middlewares(app)

app.include_router(health_router)
app.include_router(debug_router)
app.include_router(proxy_router)


@app.on_event("startup")
async def startup():
    await startup_http_client()
    logger.info("API gateway started")


@app.on_event("shutdown")
async def shutdown():
    await shutdown_http_client()
    logger.info("API gateway stopped")