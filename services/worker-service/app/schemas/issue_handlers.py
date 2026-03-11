from pydantic import BaseModel


class BaseEvent(BaseModel):
    event_type: str
    actor_id: int


class IssueCreatedEvent(BaseEvent):
    event_type: str = "issue_created"
    issue_id: int
    project_id: int


class IssueStatusChangedEvent(BaseEvent):
    event_type: str = "issue_status_changed"
    issue_id: int
    project_id: int
    old_status: str
    new_status: str


class CommentAddedEvent(BaseEvent):
    event_type: str = "comment_added"
    issue_id: int
    comment_id: int
    project_id: int