from pydantic import ValidationError

from app.core.logging import get_logger
from app.core.metrics import (
    events_unknown_total,
    events_validation_failed_total,
)
from app.notifications.delivery import deliver_notification
from app.notifications.router import (
    route_comment_added,
    route_issue_created,
    route_issue_status_changed,
)
from app.schemas.issue_handlers import (
    CommentAddedEvent,
    IssueCreatedEvent,
    IssueStatusChangedEvent,
)

logger = get_logger(__name__)


async def route_event(event: dict) -> None:
    event_type = event.get("event_type", "unknown")

    logger.info(
        "Routing worker event",
        extra={
            "event_type": event_type,
            "routing_status": "started",
        },
    )

    try:
        if event_type == "issue_created":
            parsed_event = IssueCreatedEvent(**event)
            recipients, notification = await route_issue_created(parsed_event)

        elif event_type == "issue_status_changed":
            parsed_event = IssueStatusChangedEvent(**event)
            recipients, notification = await route_issue_status_changed(parsed_event)

        elif event_type == "comment_added":
            parsed_event = CommentAddedEvent(**event)
            recipients, notification = await route_comment_added(parsed_event)

        else:
            events_unknown_total.labels(event_type=event_type).inc()
            logger.warning(
                "Unknown event type received",
                extra={
                    "event_type": event_type,
                    "routing_status": "unknown_event",
                },
            )
            return

    except ValidationError as exc:
        events_validation_failed_total.labels(event_type=event_type).inc()
        logger.error(
            "Event validation failed",
            extra={
                "event_type": event_type,
                "routing_status": "validation_failed",
                "error": str(exc),
            },
        )
        return

    await deliver_notification(
        recipients=recipients,
        payload=notification.model_dump(),
        event_type=event_type,
    )

    logger.info(
        "Worker event routed successfully",
        extra={
            "event_type": event_type,
            "routing_status": "success",
            "recipients_count": len(recipients),
        },
    )