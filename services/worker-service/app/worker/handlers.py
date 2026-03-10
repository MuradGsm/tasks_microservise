from app.worker.schemas import (
    IssueCreatedEvent,
    IssueStatusChangedEvent,
    CommentAddedEvent
)


async def handle_issue_created(event: IssueCreatedEvent) -> None:
    print("Handling issue_created:", event.model_dump())


async def handle_issue_status_changed(event: IssueStatusChangedEvent) -> None:
    print("Handling issue_status_changed:", event.model_dump())


async def handle_comment_added(event: CommentAddedEvent) -> None:
    print("Handling comment_added:", event.model_dump())


async def handle_unknown_event(event: dict) -> None:
    print("Unknown event type:", event)