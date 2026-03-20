from fastapi import HTTPException
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.issue_models import Issue, IssueCounter
from app.schemas.issue import IssueCreate, IssueOut, IssueUpdate
from app.schemas.transition import TransitionRequest, TransitionResponse
from app.schemas.internal import IssueInternalOut
from app.services.project_key import get_project_key, check_project_access
from app.services.issue_access import _validate_update, _get_issue_or_404, ALLOWED_TYPES
from app.services.workflow import validate_status, asserts_transition_allowed, ALLOWED_STATUSES
from app.services.history_utils import add_history
from app.events.publisher import publish_event
from app.core.logging import get_logger

from app.core.metrics import (
    status_changed_total,
    issues_created_total,
    issues_updated_total,
    issues_deleted_total,
)

logger = get_logger(__name__)


def _to_out(issue: Issue, project_key: str) -> IssueOut:
    return IssueOut(
        id=issue.id,
        project_id=issue.project_id,
        number=issue.number,
        key=f"{project_key}-{issue.number}",
        title=issue.title,
        description=issue.description,
        status=issue.status,
        type=issue.type,
        reporter_id=issue.reporter_id,
        assignee_id=issue.assignee_id,
        created_at=issue.created_at,
        updated_at=issue.updated_at,
    )


async def get_next_issue_number(session: AsyncSession, project_id: int) -> int:
    result = await session.execute(
        select(IssueCounter).where(IssueCounter.project_id == project_id)
    )
    counter = result.scalar_one_or_none()

    if counter is None:
        counter = IssueCounter(project_id=project_id, next_number=2)
        session.add(counter)
        await session.flush()
        return 1
    
    number = counter.next_number
    counter.next_number += 1 
    await session.flush()

    return number

class IssuesService:
    @staticmethod
    async def create(project_id: int, payload: IssueCreate, user_id: int, session: AsyncSession) -> IssueOut:
        project_key = await get_project_key(project_id, user_id)

        number = await get_next_issue_number(session, project_id)

        issue = Issue(
            project_id=project_id,
            number=number,
            title=payload.title,
            description=payload.description,
            type=payload.type,
            reporter_id=user_id,
        )

        session.add(issue)
        await session.commit()
        await session.refresh(issue)

        await publish_event(
            {
                "event_type": "issue_created",
                "issue_id": issue.id,
                "project_id": issue.project_id,
                "actor_id": user_id,
            }
        )

        issues_created_total.inc()

        logger.info(
            "Issue created",
            extra={
                "issue_id": issue.id,
                "project_id": issue.project_id,
                "user_id": user_id,
            },
        )

        return _to_out(issue, project_key)
    @staticmethod
    async def list_by_project(
        project_id: int,
        user_id: int,
        session: AsyncSession,
        status: str | None = None,
        type: str | None = None,
        assignee_id: int | None = None,
        reporter_id: int | None = None,
        q: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[IssueOut]:
        project_key = await get_project_key(project_id, user_id)

        stmt = (
            select(Issue)
            .where(Issue.project_id == project_id, Issue.is_deleted == False)  # noqa: E712
        )

        if status:
            status = status.strip().upper()
            if status not in ALLOWED_STATUSES:
                raise HTTPException(status_code=422, detail="Invalid status")
            stmt = stmt.where(Issue.status == status)

        if type:
            type = type.strip().upper()
            if type not in ALLOWED_TYPES:
                raise HTTPException(status_code=422, detail="Invalid type")
            stmt = stmt.where(Issue.type == type)

        if assignee_id is not None:
            stmt = stmt.where(Issue.assignee_id == assignee_id)

        if reporter_id is not None:
            stmt = stmt.where(Issue.reporter_id == reporter_id)

        if q:
            q = q.strip()
            if q:
                pattern = f"%{q}%"
                stmt = stmt.where(
                    or_(
                        Issue.title.ilike(pattern),
                        Issue.description.ilike(pattern),
                    )
                )

        stmt = stmt.order_by(Issue.number.asc()).limit(limit).offset(offset)

        result = await session.execute(stmt)
        issues = result.scalars().all()

        return [_to_out(i, project_key) for i in issues]

    @staticmethod
    async def get(issue_id: int, user_id: int, session: AsyncSession) -> IssueOut:
        issue = await _get_issue_or_404(issue_id, session)

        project_key = await get_project_key(issue.project_id, user_id)
        return _to_out(issue, project_key)

    @staticmethod
    async def update(issue_id: int, payload: IssueUpdate, user_id: int, session: AsyncSession) -> IssueOut:
        issue = await _get_issue_or_404(issue_id, session)

        project_key = await get_project_key(issue.project_id, user_id)

        data = payload.model_dump(exclude_unset=True)
        _validate_update(data)

        if "assignee_id" in data and data["assignee_id"] is not None:
            logger.info(
                "Validating assignee access",
                extra={
                    "issue_id": issue.id,
                    "project_id": issue.project_id,
                    "user_id": user_id,
                },
            )

            has_access = await check_project_access(issue.project_id, data["assignee_id"])

            logger.info(
                "Assignee access validation finished",
                extra={
                    "issue_id": issue.id,
                    "project_id": issue.project_id,
                    "user_id": user_id,
                    "assignee_id": data["assignee_id"],
                    "has_access": has_access,
                },
            )

            if not has_access:
                raise HTTPException(
                    status_code=400,
                    detail="Assignee must be a project member or owner",
                )
        updated = False
        for field, new_value in data.items():

            old_value = getattr(issue, field)

            if old_value == new_value:
                continue
            
            add_history(
                issue_id=issue.id,
                actor_id=user_id,
                field=field,
                old_value=old_value,
                new_value=new_value,
                session=session,
            )
            updated = True
            setattr(issue, field, new_value)

        if not updated:
            return _to_out(issue, project_key)

        await session.commit()
        await session.refresh(issue)

        issues_updated_total.inc()
        await publish_event(
            {
                "event_type": "issue_updated",
                "issue_id": issue.id,
                "project_id": issue.project_id,
                "actor_id": user_id,
            }
        )

        return _to_out(issue, project_key)

    @staticmethod
    async def delete(issue_id: int, user_id: int, session: AsyncSession) -> None:
        issue = await _get_issue_or_404(issue_id, session)

        # access check
        await get_project_key(issue.project_id, user_id)

        issue.is_deleted = True

        await session.commit()
        issues_deleted_total.inc()
        await publish_event(
            {
                "event_type": "issue_deleted",
                "issue_id": issue.id,
                "project_id": issue.project_id,
                "actor_id": user_id,
            }
        )
        logger.info(
            "Issue soft deleted",
            extra={
                "issue_id": issue.id,
                "project_id": issue.project_id,
                "user_id": user_id,
            },
        )

    @staticmethod
    async def transition(issue_id: int, payload: TransitionRequest, user_id: int, session: AsyncSession) -> TransitionResponse:
        issue = await _get_issue_or_404(issue_id, session)

        await get_project_key(issue.project_id, user_id)

        from_status = issue.status
        to_status = validate_status(payload.to_status)
        
        asserts_transition_allowed(from_status, to_status)

        issue.status = to_status
        add_history(
            issue_id=issue.id,
            actor_id=user_id,
            field="status",
            old_value=from_status,
            new_value=to_status,
            session=session,
        )
        await session.commit()
        await session.refresh(issue)

        status_changed_total.labels(
            from_status=from_status,
            to_status=to_status,
        ).inc()
        
        await publish_event(
            {

                "event_type": "issue_status_changed",
                "issue_id": issue_id,
                "project_id": issue.project_id,
                "actor_id": user_id,
                "old_status": from_status,
                "new_status": to_status
            }
        )
        logger.info(
            "Issue status changed",
            extra={
                "issue_id": issue.id,
                "project_id": issue.project_id,
                "user_id": user_id,
                "from_status": from_status,
                "to_status": to_status,
            },
        )
        return TransitionResponse(
            issue_id=issue.id,
            from_status=from_status,
            to_status=to_status,
        )

    @staticmethod
    async def get_internal(issue_id: int, session: AsyncSession) -> IssueInternalOut:
        issue = await _get_issue_or_404(issue_id, session)

        return IssueInternalOut(
            id=issue.id,
            project_id=issue.project_id,
            reporter_id=issue.reporter_id,
            assignee_id=issue.assignee_id,
        )