import time
import uuid

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

from app.clients.identity import is_public_path, validate_token
from app.core.logging import get_logger
from app.core.metrics import auth_failures_total, http_requests_custom_total
from app.core.request_context import set_request_id

logger = get_logger("app.middleware.auth")


def register_middlewares(app: FastAPI) -> None:
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
                        identity_resp = await validate_token(token, request_id)
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