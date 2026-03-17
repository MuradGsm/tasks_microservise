import os
import time
import uuid

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

from app.core.logging import get_logger, setup_logging
from app.core.request_context import set_request_id
from app.core.metrics import (
    http_requests_custom_total, 
    auth_failures_total, 
    upstream_requests_total
)

setup_logging()
logger = get_logger("app.main")

app = FastAPI(title="SJira API Gateway")
Instrumentator().instrument(app).expose(app)


IDENTITY_URL = os.getenv("IDENTITY_URL", "http://identity-service:8000")
PROJECT_URL = os.getenv("PROJECT_URL", "http://project-service:8000")
ISSUE_URL = os.getenv("ISSUE_URL", "http://issue-service:8000")
NOTIFICATIONS_URL = os.getenv("NOTIFICATIONS_URL", "http://notifications-service:8000")


def is_public_path(path: str) -> bool:
    public_paths = {
        "/health",
        "/metrics",
        "/public/ping",
        "/auth/token/",
        "/auth/token/refresh/",
    }
    public_prefixes = ("/docs", "/openapi.json", "/redoc")
    return path in public_paths or path.startswith(public_prefixes)


@app.middleware("http")
async def logging_and_auth_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-Id") or str(uuid.uuid4())
    set_request_id(request_id)
    request.state.request_id = request_id

    start_time = time.time()

    logger.info(
        "HTTP request started",
        extra={
            "path": request.url.path,
            "method": request.method,
        },
    )

    response: Response | JSONResponse

    try:
        if is_public_path(request.url.path):
            response = await call_next(request)
        else:
            auth_header = request.headers.get("authorization", "")
            if not auth_header.lower().startswith("bearer "):
                logger.warning(
                    "Authentication failed: missing bearer token",
                    extra={
                        "path": request.url.path,
                        "method": request.method,
                    },
                )
                auth_failures_total.labels(
                    reason="missing_bearer",
                    path=request.url.path,
                ).inc()
                response = JSONResponse(
                    {"detail": "Missing Bearer token"},
                    status_code=401,
                )
            else:
                token = auth_header.split(" ", 1)[1].strip()

                logger.info(
                    "Token validation requested",
                    extra={
                        "path": request.url.path,
                        "method": request.method,
                        "upstream_service": "identity-service",
                    },
                )

                try:
                    async with httpx.AsyncClient(timeout=5.0) as client:
                        identity_resp = await client.get(
                            f"{IDENTITY_URL}/auth/me/",
                            headers={
                                "Authorization": f"Bearer {token}",
                                "X-Request-Id": request_id,
                            },
                        )
                except httpx.RequestError:
                    logger.exception(
                        "Identity service unavailable",
                        extra={
                            "path": request.url.path,
                            "method": request.method,
                            "upstream_service": "identity-service",
                        },
                    )
                    auth_failures_total.labels(
                        reason="identity_unavailable",
                        path=request.url.path,
                    ).inc()
                    response = JSONResponse(
                        {"detail": "Identity service unavailable"},
                        status_code=503,
                    )
                else:
                    logger.info(
                        "Token validation response received",
                        extra={
                            "path": request.url.path,
                            "method": request.method,
                            "upstream_service": "identity-service",
                            "upstream_status": identity_resp.status_code,
                        },
                    )

                    if identity_resp.status_code != 200:
                        logger.warning(
                            "Authentication failed: invalid token",
                            extra={
                                "path": request.url.path,
                                "method": request.method,
                                "upstream_service": "identity-service",
                                "upstream_status": identity_resp.status_code,
                            },
                        )
                        auth_failures_total.labels(
                            reason="invalid_token",
                            path=request.url.path,
                        ).inc()
                        response = JSONResponse(
                            {
                                "detail": "Invalid token",
                                "identity_status": identity_resp.status_code,
                                "identity_body": identity_resp.text,
                            },
                            status_code=401,
                        )
                    else:
                        data = identity_resp.json()
                        user_id = data.get("id") or data.get("user_id")

                        if user_id is None:
                            logger.error(
                                "Identity response missing user id",
                                extra={
                                    "path": request.url.path,
                                    "method": request.method,
                                    "upstream_service": "identity-service",
                                },
                            )
                            auth_failures_total.labels(
                                reason="missing_user_id",
                                path=request.url.path,
                            ).inc()
                            response = JSONResponse(
                                {"detail": "Identity response missing user id"},
                                status_code=500,
                            )
                        else:
                            request.state.user_id = str(user_id)

                            logger.info(
                                "Authentication succeeded",
                                extra={
                                    "path": request.url.path,
                                    "method": request.method,
                                    "user_id": int(user_id),
                                },
                            )

                            response = await call_next(request)

    except Exception:
        duration_ms = int((time.time() - start_time) * 1000)
        logger.exception(
            "HTTP request failed",
            extra={
                "path": request.url.path,
                "method": request.method,
                "duration_ms": duration_ms,
            },
        )
        raise

    duration_ms = int((time.time() - start_time) * 1000)

    response.headers["X-Request-Id"] = request_id

    logger.info(
        "HTTP request completed",
        extra={
            "path": request.url.path,
            "method": request.method,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
        },
    )
    http_requests_custom_total.labels(
        method=request.method,
        path=request.url.path,
        status=str(response.status_code),
    ).inc()

    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    logger.info("API gateway started")


@app.on_event("shutdown")
async def shutdown():
    logger.info("API gateway stopped")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "api-gateway"}


@app.get("/public/ping")
async def public_ping():
    return {"pong": "public"}


@app.get("/private/ping")
async def private_ping(request: Request):
    return {
        "pong": "private",
        "user_id": getattr(request.state, "user_id", None),
    }


async def proxy_request(
    request: Request,
    upstream_url: str,
    *,
    upstream_service: str,
) -> Response:
    body = await request.body()

    headers = {}
    if request.headers.get("content-type"):
        headers["content-type"] = request.headers["content-type"]

    headers["X-User-Id"] = getattr(request.state, "user_id", "")
    headers["X-Request-Id"] = getattr(request.state, "request_id", "")

    logger.info(
        "Upstream request started",
        extra={
            "path": request.url.path,
            "method": request.method,
            "user_id": int(request.state.user_id) if hasattr(request.state, "user_id") else None,
            "upstream_service": upstream_service,
        },
    )

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            upstream_resp = await client.request(
                method=request.method,
                url=upstream_url,
                params=request.query_params,
                content=body,
                headers=headers,
            )
    except httpx.RequestError:
        logger.exception(
            "Upstream request failed",
            extra={
                "path": request.url.path,
                "method": request.method,
                "user_id": int(request.state.user_id),
                "upstream_service": upstream_service,
            },
        )
        upstream_requests_total.labels(
            service=upstream_service,
            status="error"
        ).inc()
        return JSONResponse(
            {"detail": f"{upstream_service} unavailable"},
            status_code=503,
        )

    logger.info(
        "Upstream response received",
        extra={
            "path": request.url.path,
            "method": request.method,
            "user_id": int(request.state.user_id),
            "upstream_service": upstream_service,
            "upstream_status": upstream_resp.status_code,
        },
    )

    upstream_requests_total.labels(
        service=upstream_service,
        status=str(upstream_resp.status_code)
    ).inc()

    response = Response(
        content=upstream_resp.content,
        status_code=upstream_resp.status_code,
        media_type=upstream_resp.headers.get("content-type"),
    )
    response.headers["X-Request-Id"] = getattr(request.state, "request_id", "")
    return response


@app.api_route("/projects/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_projects(request: Request, path: str):
    upstream_url = f"{PROJECT_URL}/v1/projects/{path}"
    return await proxy_request(
        request,
        upstream_url,
        upstream_service="project-service",
    )


@app.get("/private/whoami")
async def whoami(request: Request):
    return {"user_id": getattr(request.state, "user_id", None)}


@app.api_route("/issues/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_issues(request: Request, path: str):
    upstream_url = f"{ISSUE_URL}/v1/issues/{path}"
    return await proxy_request(
        request,
        upstream_url,
        upstream_service="issue-service",
    )


@app.api_route("/notifications", methods=["GET"])
@app.api_route("/notifications/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_notifications(request: Request, path: str = ""):
    upstream_url = f"{NOTIFICATIONS_URL}/v1/notifications"
    if path:
        upstream_url = f"{upstream_url}/{path}"

    return await proxy_request(
        request,
        upstream_url,
        upstream_service="notifications-service",
    )

@app.api_route("/auth/{path:path}", methods=["GET", "POST"])
async def proxy_auth(request: Request, path: str):
    upstream_url = f"{IDENTITY_URL}/auth/{path}"
    return await proxy_request(
        request,
        upstream_url,
        upstream_service="identity-service",
    )