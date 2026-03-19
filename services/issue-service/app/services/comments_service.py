from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.issue import Issue, IssueComment
from app.schemas.comment import CommentCreate, CommentOut
from app.services.project_key import get_project_key
from app.services.access_issue import _get_issue_or_404
from app.events.publisher import publish_event
from app.core.metrics import comments_created_total

def _to_out(c: IssueComment) -> CommentOut:
    return CommentOut(
        id=c.id,
        issue_id=c.issue_id,
        author_id=c.author_id,
        text=c.text,
        created_at=c.created_at,
    )


class CommentService:
    @staticmethod
    async def create(issue_id: int, payload: CommentCreate, user_id: int, session: AsyncSession) -> CommentOut:
        issue = await _get_issue_or_404(issue_id, session)

        await get_project_key(issue.project_id, user_id)

        comment = IssueComment(issue_id=issue_id, author_id=user_id, text=payload.text)

        session.add(comment)
        await session.commit()
        await session.refresh(comment)

        comments_created_total.inc()

        await publish_event(
            {
                "event_type": "comment_added",
                "issue_id": issue_id,
                "comment_id": comment.id,
                "project_id": issue.project_id,
                "actor_id": user_id,
            }
        )

        return _to_out(comment)
    
    @staticmethod
    async def list(issue_id: int, user_id: int, session: AsyncSession, limit: int = 20, offset: int = 0) -> list[CommentOut]:
        issue = await _get_issue_or_404(issue_id, session)

        await get_project_key(issue.project_id, user_id)

        result = await session.execute(
            select(IssueComment)
            .where(IssueComment.issue_id == issue_id)
            .order_by(IssueComment.id.asc())
            .limit(limit)
            .offset(offset)
        )
        comments = result.scalars().all()
        return [_to_out(c) for c in comments]