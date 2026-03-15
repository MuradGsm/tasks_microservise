from app.core.logging import get_logger
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
from app.worker.delivery import send_notification_with_retry

logger = get_logger(__name__)


async def handle_issue_created(event: IssueCreatedEvent) -> None:
    event_context = event.model_dump()

    logger.info("Handling issue_created event", extra=event_context)

    recipients, notification = await route_issue_created(event)

    logger.info(
        "Issue_created notification routing completed",
        extra={
            **event_context,
            "recipients_count": len(recipients),
        },
    )

    for user_id in recipients:
        logger.info(
            "Starting notification delivery",
            extra={
                **event_context,
                "recipient_id": user_id,
            },
        )

        await send_notification_with_retry(
            user_id=user_id,
            payload=notification.model_dump(),
            event_context=event_context,
        )

    logger.info(
        "Issue_created event handled successfully",
        extra={
            **event_context,
            "recipients_count": len(recipients),
        },
    )


async def handle_issue_status_changed(event: IssueStatusChangedEvent) -> None:
    event_context = event.model_dump()

    logger.info("Handling issue_status_changed event", extra=event_context)

    recipients, notification = await route_issue_status_changed(event)

    logger.info(
        "Issue_status_changed notification routing completed",
        extra={
            **event_context,
            "recipients_count": len(recipients),
        },
    )

    for user_id in recipients:
        logger.info(
            "Starting notification delivery",
            extra={
                **event_context,
                "recipient_id": user_id,
            },
        )

        await send_notification_with_retry(
            user_id=user_id,
            payload=notification.model_dump(),
            event_context=event_context,
        )

    logger.info(
        "Issue_status_changed event handled successfully",
        extra={
            **event_context,
            "recipients_count": len(recipients),
        },
    )


async def handle_comment_added(event: CommentAddedEvent) -> None:
    event_context = event.model_dump()

    logger.info("Handling comment_added event", extra=event_context)

    recipients, notification = await route_comment_added(event)

    logger.info(
        "Comment_added notification routing completed",
        extra={
            **event_context,
            "recipients_count": len(recipients),
        },
    )

    for user_id in recipients:
        logger.info(
            "Starting notification delivery",
            extra={
                **event_context,
                "recipient_id": user_id,
            },
        )

        await send_notification_with_retry(
            user_id=user_id,
            payload=notification.model_dump(),
            event_context=event_context,
        )

    logger.info(
        "Comment_added event handled successfully",
        extra={
            **event_context,
            "recipients_count": len(recipients),
        },
    )


async def handle_unknown_event(event: dict) -> None:
    logger.warning(
        "Unknown event skipped",
        extra=event,
    )