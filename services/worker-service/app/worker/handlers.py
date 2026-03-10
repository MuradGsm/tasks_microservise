from app.clients.notifications_client import push_notification
from app.worker.schemas import (
    CommentAddedEvent,
    IssueCreatedEvent,
    IssueStatusChangedEvent,
)


async def handle_issue_created(event: IssueCreatedEvent) -> None:
    print("Handling issue_created:", event.model_dump())

    await push_notification(
        user_id=event.actor_id,
        payload={
            "type": "issue_created",
            "issue_id": event.issue_id,
            "project_id": event.project_id,
            "message": f"Issue #{event.issue_id} was created",
        },
    )


async def handle_issue_status_changed(event: IssueStatusChangedEvent) -> None:
    print("Handling issue_status_changed:", event.model_dump())

    await push_notification(
        user_id=event.actor_id,
        payload={
            "type": "issue_status_changed",
            "issue_id": event.issue_id,
            "project_id": event.project_id,
            "old_status": event.old_status,
            "new_status": event.new_status,
            "message": f"Issue moved from {event.old_status} to {event.new_status}",
        },
    )


async def handle_comment_added(event: CommentAddedEvent) -> None:
    print("Handling comment_added:", event.model_dump())

    await push_notification(
        user_id=event.actor_id,
        payload={
            "type": "comment_added",
            "issue_id": event.issue_id,
            "project_id": event.project_id,
            "comment_id": event.comment_id,
            "message": f"New comment added to issue #{event.issue_id}",
        },
    )


async def handle_unknown_event(event: dict) -> None:
    print("Unknown event type:", event)