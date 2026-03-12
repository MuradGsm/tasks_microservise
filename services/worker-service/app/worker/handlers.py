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


async def handle_issue_created(event: IssueCreatedEvent) -> None:
    print("Handling issue_created:", event.model_dump())

    recipients, notification = await route_issue_created(event)

    for user_id in recipients:
        await send_notification_with_retry(
            user_id=user_id,
            payload=notification.model_dump(),
        )


async def handle_issue_status_changed(event: IssueStatusChangedEvent) -> None:
    print("Handling issue_status_changed:", event.model_dump())

    recipients, notification = await route_issue_status_changed(event)

    for user_id in recipients:
        await send_notification_with_retry(
            user_id=user_id,
            payload=notification.model_dump(),
        )


async def handle_comment_added(event: CommentAddedEvent) -> None:
    print("Handling comment_added:", event.model_dump())

    recipients, notification = await route_comment_added(event)

    for user_id in recipients:
        await send_notification_with_retry(
            user_id=user_id,
            payload=notification.model_dump(),
        )


async def handle_unknown_event(event: dict) -> None:
    print("Unknown event type:", event)