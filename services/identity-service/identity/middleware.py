import time
import uuid

from identity.logging import get_logger
from identity.request_context import set_request_id

logger = get_logger("identity.middleware")


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = request.headers.get("X-Request-Id") or str(uuid.uuid4())
        set_request_id(request_id)
        request.request_id = request_id

        start_time = time.time()

        logger.info(
            "HTTP request started",
            extra={
                "path": request.path,
                "method": request.method,
            },
        )

        try:
            response = self.get_response(request)
        except Exception:
            duration_ms = int((time.time() - start_time) * 1000)

            logger.exception(
                "HTTP request failed",
                extra={
                    "path": request.path,
                    "method": request.method,
                    "duration_ms": duration_ms,
                },
            )
            raise

        duration_ms = int((time.time() - start_time) * 1000)

        response["X-Request-Id"] = request_id

        logger.info(
            "HTTP request completed",
            extra={
                "path": request.path,
                "method": request.method,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )

        return response