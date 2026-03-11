from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_session
from app.schemas.internal import IssueInternalOut
from app.services.issues_service import IssuesService

router = APIRouter(prefix="/internal", tags=["Internal"])


@router.get("/issues/{issue_id}", response_model=IssueInternalOut)
async def get_issue_internal(
    issue_id: int,
    session: AsyncSession = Depends(get_session),
):
    return await IssuesService.get_internal(issue_id, session)