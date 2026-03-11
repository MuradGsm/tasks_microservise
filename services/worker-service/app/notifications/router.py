from app.schemas.notification import NotificationPayload
from app.schemas.issue_handlers import (
    CommentAddedEvent,
    IssueCreatedEvent,
    IssueStatusChangedEvent,
)

from app.notifications.recipients import (
    resolve_comment_added_recipients,
    resolve_issue_created_recipients,
    resolve_issue_status_changed_recipients,
)


def build_issue_created_notification(event: IssueCreatedEvent) -> NotificationPayload:
    return NotificationPayload(
        type="issue_created",
        title="Issue created",
        message=f"Issue #{event.issue_id} was created",
        entity_type="issue",
        entity_id=event.issue_id,
        project_id=event.project_id,
    )


def build_issue_status_changed_notification(event: IssueStatusChangedEvent) -> NotificationPayload:
    return NotificationPayload(
        type="issue_status_changed",
        title="Issue status changed",
        message=f"Issue moved from {event.old_status} to {event.new_status}",
        entity_type="issue",
        entity_id=event.issue_id,
        project_id=event.project_id,
    )


def build_comment_added_notification(event: CommentAddedEvent) -> NotificationPayload:
    return NotificationPayload(
        type="comment_added",
        title="Comment added",
        message=f"New comment added to issue #{event.issue_id}",
        entity_type="issue",
        entity_id=event.issue_id,
        project_id=event.project_id,
    )


def route_issue_created(event: IssueCreatedEvent) -> tuple[list[int], NotificationPayload]:
    recipients = resolve_issue_created_recipients(event)
    notification = build_issue_created_notification(event)
    return recipients, notification


async def route_issue_status_changed(event: IssueStatusChangedEvent):

    recipients = await resolve_issue_status_changed_recipients(event)

    notification = build_issue_status_changed_notification(event)

    return recipients, notification


def route_comment_added(event: CommentAddedEvent) -> tuple[list[int], NotificationPayload]:
    recipients = resolve_comment_added_recipients(event)
    notification = build_comment_added_notification(event)
    return recipients, notification