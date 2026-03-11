from app.clients.notifications_client import get_issue

from app.schemas.issue_handlers import (
    CommentAddedEvent,
    IssueCreatedEvent,
    IssueStatusChangedEvent
)

def resolve_issue_created_recipients(event: IssueCreatedEvent) -> list[int]:
    return [event.actor_id]


async def resolve_issue_status_changed_recipients(
    event: IssueStatusChangedEvent,
) -> list[int]:

    issue = await get_issue(event.issue_id)

    reporter = issue["reporter_id"]
    assignee = issue["assignee_id"]

    users = [reporter, assignee]

    # remove None
    users = [u for u in users if u is not None]

    # remove duplicates
    users = list(set(users))

    return users


def resolve_comment_added_recipients(event: CommentAddedEvent) -> list[int]:
    return [event.actor_id]