from app.clients.issue_client import get_issue
from app.core.logging import get_logger
from app.schemas.issue_handlers import (
    CommentAddedEvent,
    IssueCreatedEvent,
    IssueStatusChangedEvent,
)

logger = get_logger(__name__)


def _normalize_users(users: list[int | None], actor_id: int) -> list[int]:
    users = [u for u in users if u is not None]
    users = list(set(users))
    users = [u for u in users if u != actor_id]
    return users


async def resolve_issue_created_recipients(event: IssueCreatedEvent) -> list[int]:
    logger.info(
        "Resolving recipients for issue_created",
        extra=event.model_dump(),
    )

    issue = await get_issue(event.issue_id)
    assignee = issue["assignee_id"]

    recipients = _normalize_users([assignee], event.actor_id)

    logger.info(
        "Recipients resolved for issue_created",
        extra={
            **event.model_dump(),
            "recipients_count": len(recipients),
            "recipients": recipients,
        },
    )

    return recipients


async def resolve_issue_status_changed_recipients(
    event: IssueStatusChangedEvent,
) -> list[int]:
    logger.info(
        "Resolving recipients for issue_status_changed",
        extra=event.model_dump(),
    )

    issue = await get_issue(event.issue_id)

    reporter = issue["reporter_id"]
    assignee = issue["assignee_id"]

    recipients = _normalize_users([reporter, assignee], event.actor_id)

    logger.info(
        "Recipients resolved for issue_status_changed",
        extra={
            **event.model_dump(),
            "recipients_count": len(recipients),
            "recipients": recipients,
        },
    )

    return recipients


async def resolve_comment_added_recipients(event: CommentAddedEvent) -> list[int]:
    logger.info(
        "Resolving recipients for comment_added",
        extra=event.model_dump(),
    )

    issue = await get_issue(event.issue_id)

    reporter = issue["reporter_id"]
    assignee = issue["assignee_id"]

    recipients = _normalize_users([reporter, assignee], event.actor_id)

    logger.info(
        "Recipients resolved for comment_added",
        extra={
            **event.model_dump(),
            "recipients_count": len(recipients),
            "recipients": recipients,
        },
    )

    return recipients