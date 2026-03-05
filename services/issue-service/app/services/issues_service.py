from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.issue import Issue, IssueCounter
from app.schemas.issue import IssueCreate, IssueOut, IssueUpdate
from app.schemas.transition import TransitionRequest, TransitionResponse
from app.services.project_key import get_project_key
from app.services.access_issue import _validate_update, _get_issue_or_404
from app.services.workflow import validate_status, asserts_transition_allowed

def _to_out(issue: Issue, project_key: str) -> IssueOut:
    return IssueOut(
        id=issue.id,
        project_id=issue.project_id,
        number=issue.number,
        key=f"{project_key}-{issue.number}",
        title=issue.title,
        status=issue.status,
        type=issue.type,
        reporter_id=issue.reporter_id,
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

        return _to_out(issue, project_key)

    @staticmethod
    async def list_by_project(project_id: int, user_id: int, session: AsyncSession) -> list[IssueOut]:
        project_key = await get_project_key(project_id, user_id)

        result = await session.execute(
            select(Issue)
            .where(Issue.project_id == project_id, Issue.is_deleted == False)  # noqa: E712
            .order_by(Issue.number.asc())
        )
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

        for field, value in data.items():
            setattr(issue, field, value)

        await session.commit()
        await session.refresh(issue)

        return _to_out(issue, project_key)

    @staticmethod
    async def delete(issue_id: int, user_id: int, session: AsyncSession) -> None:
        issue = await _get_issue_or_404(issue_id, session)

        # access check
        await get_project_key(issue.project_id, user_id)

        issue.is_deleted = True
        await session.commit()

    @staticmethod
    async def transition(issue_id: int, payload: TransitionRequest, user_id: int, session: AsyncSession) -> TransitionResponse:
        issue = await _get_issue_or_404(issue_id, session)

        await get_project_key(issue.project_id, user_id)

        from_status = issue.status
        to_status = validate_status(payload.to_status)
        
        asserts_transition_allowed(from_status, to_status)

        issue.status = to_status
        await session.commit()
        await session.refresh(issue)

        return TransitionResponse(
            issue_id=issue.id,
            from_status=from_status,
            to_status=to_status,
        )