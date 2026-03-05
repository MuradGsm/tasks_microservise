from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.issue import IssueHistory, Issue
from app.schemas.history import HistoryOut
from app.services.project_key import get_project_key
from app.services.access_issue import _get_issue_or_404

def _to_out(h: IssueHistory) -> HistoryOut:
    return HistoryOut(
        id=h.id,
        issue_id=h.issue_id,
        actor_id=h.actor_id,
        field=h.field,
        old_value=h.old_value,
        new_value=h.new_value,
        created_at=h.created_at,
    )

class HistoryService:
    @staticmethod
    async def list(
        issue_id: int,
        user_id: int,
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0,
    ) -> list[HistoryOut]:
        issue = await _get_issue_or_404(issue_id, session)

        # access check
        await get_project_key(issue.project_id, user_id)

        result = await session.execute(
            select(IssueHistory)
            .where(IssueHistory.issue_id == issue_id)
            .order_by(IssueHistory.id.desc())
            .limit(limit)
            .offset(offset)
        )
        rows = result.scalars().all()
        return [_to_out(r) for r in rows]