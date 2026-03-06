from fastapi import APIRouter, Depends, Header, Response, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_session
from app.schemas.issue import IssueCreate, IssueOut, IssueUpdate
from app.services.issues_service import IssuesService

router = APIRouter(tags=["Issues"])


@router.post("/projects/{project_id}/issues", response_model=IssueOut, status_code=201)
async def create_issue(
    project_id: int,
    payload: IssueCreate,
    x_user_id: int = Header(..., alias="X-User-Id"),
    session: AsyncSession = Depends(get_session),
):
    return await IssuesService.create(project_id, payload, x_user_id, session)


@router.get("/projects/{project_id}/issues", response_model=list[IssueOut])
async def list_issues(
    project_id: int,
    x_user_id: int = Header(..., alias="X-User-Id"),
    status: str | None = Query(None),
    type: str | None = Query(None),
    assignee_id: int | None = Query(None),
    reporter_id: int|None = Query(None),
    q: str| None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
):
    return await IssuesService.list_by_project( 
        project_id,
        x_user_id,
        session,
        status=status,
        type=type,
        assignee_id=assignee_id,
        reporter_id=reporter_id,
        q=q,
        limit=limit,
        offset=offset,)


@router.get("/issues/{issue_id}", response_model=IssueOut)
async def get_issue(
    issue_id: int,
    x_user_id: int = Header(..., alias="X-User-Id"),
    session: AsyncSession = Depends(get_session),
):
    return await IssuesService.get(issue_id, x_user_id, session)


@router.patch("/issues/{issue_id}", response_model=IssueOut)
async def update_issue(
    issue_id: int,
    payload: IssueUpdate,
    x_user_id: int = Header(..., alias="X-User-Id"),
    session: AsyncSession = Depends(get_session),
):
    return await IssuesService.update(issue_id, payload, x_user_id, session)


@router.delete("/issues/{issue_id}", status_code=204)
async def delete_issue(
    issue_id: int,
    x_user_id: int = Header(..., alias="X-User-Id"),
    session: AsyncSession = Depends(get_session),
):
    await IssuesService.delete(issue_id, x_user_id, session)
    return Response(status_code=204)