import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.request_context import set_request_id
from app.core.logging import get_logger


logger = get_logger("app.middleware.logging")


class LoggingMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        request_id = request.headers.get("X-Request-Id") or str(uuid.uuid4())
        set_request_id(request_id)

        start_time = time.time()

        logger.info(
            "HTTP request started",
            extra={
                "path": request.url.path,
                "method": request.method,
            },
        )

        try:
            response: Response = await call_next(request)

        except Exception as exc:

            duration_ms = int((time.time() - start_time) * 1000)

            logger.exception(
                "HTTP request failed",
                extra={
                    "path": request.url.path,
                    "method": request.method,
                    "duration_ms": duration_ms,
                },
            )

            raise exc

        duration_ms = int((time.time() - start_time) * 1000)

        logger.info(
            "HTTP request completed",
            extra={
                "path": request.url.path,
                "method": request.method,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )

        response.headers["X-Request-Id"] = request_id

        return response