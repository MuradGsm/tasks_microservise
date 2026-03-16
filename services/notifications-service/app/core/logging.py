import json
import logging
import sys
from datetime import datetime, timezone

from app.core.request_context import get_request_id

SERVICE_NAME = "notifications-service"

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
        if request_id is not None:
            log_data["request_id"] = request_id
        
        extra_fields = (
            "request_id",
            "user_id",
            "notification_id",
            "project_id",
            "entity_id",
            "entity_type",
            "path",
            "method",
            "status_code",
            "duration_ms",
            "created",
            "is_read",
            "connection_count",
            "delivered_to",
            "delivery_status",
        )
        
        for field in extra_fields:
            value = getattr(record, field, None)
            if value is not None:
                log_data[field] = value

        if record.exc_info is not None:
            exc_type, exc_value, exc_tb = record.exc_info
            if exc_type is not None:
                log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, ensure_ascii=False)

def setup_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()
    root_logger.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)