from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.issue_models import Issue

ALLOWED_TYPES = {"TASK", "BUG", "STORY"}


def _validate_update(data: dict) -> None:
    if "type" in data and data["type"] not in ALLOWED_TYPES:
        raise HTTPException(status_code=422, detail="Invalid type")


async def _get_issue_or_404(issue_id: int, session: AsyncSession) -> Issue:
    result = await session.execute(select(Issue).where(Issue.id == issue_id))
    issue = result.scalar_one_or_none()
    if issue is None or issue.is_deleted:
        raise HTTPException(status_code=404, detail="Issue not found")
    return issue