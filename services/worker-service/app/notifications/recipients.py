from app.clients.issue_client import get_issue

from app.schemas.issue_handlers import (
    CommentAddedEvent,
    IssueCreatedEvent,
    IssueStatusChangedEvent,
)


def _normalize_users(users: list[int | None], actor_id: int) -> list[int]:
    users = [u for u in users if u is not None]
    users = list(set(users))
    users = [u for u in users if u != actor_id]
    return users

async def resolve_issue_created_recipients(event: IssueCreatedEvent) -> list[int]:
    issue = await get_issue(event.issue_id)

    asignee = issue["asignee_id"]

    return _normalize_users([asignee], event.actor_id)


async def resolve_issue_status_changed_recipients(
    event: IssueStatusChangedEvent,
) -> list[int]:
    issue = await get_issue(event.issue_id)

    reporter = issue["reporter_id"]
    assignee = issue["assignee_id"]

    return _normalize_users([reporter, assignee], event.actor_id)


async def resolve_comment_added_recipients(event: CommentAddedEvent) -> list[int]:
    issue = await get_issue(event.issue_id)

    reporter = issue["reporter_id"]
    assignee = issue["assignee_id"]

    return _normalize_users([reporter, assignee], event.actor_id)