from pydantic import ValidationError

from app.worker.handlers import (
    handle_comment_added,
    handle_issue_created,
    handle_issue_status_changed,
    handle_unknown_event,
)

from app.schemas.issue_handlers import (
    CommentAddedEvent,
    IssueCreatedEvent,
    IssueStatusChangedEvent
)

EVENT_SCHEMAS = {
    "issue_created": IssueCreatedEvent,
    "issue_status_changed": IssueStatusChangedEvent,
    "comment_added": CommentAddedEvent,
}

EVENT_HANDLERS = {
    "issue_created": handle_issue_created,
    "issue_status_changed": handle_issue_status_changed,
    "comment_added": handle_comment_added,
}

async def route_event(event: dict) -> None:
    event_type = event.get("event_type")

    schema = EVENT_SCHEMAS.get(event_type)
    handler = EVENT_HANDLERS.get(event_type)

    if not schema or not handler:
        await handle_unknown_event(event)
        return
    
    try:
        validated_event = schema.model_validate(event)
    except ValidationError as e:
        print(f"Event validation failed for type={event_type}: {e}")
        return

    await handler(validated_event)

    