import json
import logging
import sys
from datetime import datetime, timezone

from app.core.request_context import get_request_id

SERVICE_NAME = "project-service"


class JsonFormatter(logging.Formatter):

    def format(self, record: logging.LogRecord) -> str:

        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "service": SERVICE_NAME,
            "logger": record.name,
            "message": record.getMessage(),
        }

        request_id = get_request_id()
        if request_id:
            log_data["request_id"] = request_id

        whitelist = [
            "user_id",
            "project_id",
            "member_id",
            "path",
            "method",
            "status_code",
            "duration_ms"
        ]

        for field in whitelist:
            value = getattr(record, field, None)
            if value is not None:
                log_data[field] = value

        return json.dumps(log_data)


def setup_logging():

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    root = logging.getLogger()
    root.setLevel(logging.INFO)

    root.handlers.clear()
    root.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)