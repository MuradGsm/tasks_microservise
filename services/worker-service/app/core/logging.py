import json
import logging
import sys
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "service": "worker-service",
            "logger": record.name,
            "message": record.getMessage(),
        }

        optional_fields = [
            "event_type",
            "issue_id",
            "project_id",
            "actor_id",
            "comment_id",
            "recipient_id",
            "retry_attempt",
            "max_attempts",
            "delivery_status",
            "status_code",
            "duration_ms",
            "queue",
            "routing_status",
            "recipients_count",
            "recipients",
            "error",
            "target_service",
            "url",
        ]

        for field in optional_fields:
            value = getattr(record, field, None)
            if value is not None:
                log_data[field] = value

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, ensure_ascii=False)


def configure_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)