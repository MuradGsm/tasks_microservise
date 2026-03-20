from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_session
from app.schemas.transition import TransitionRequest, TransitionResponse
from app.services.issues_service import IssuesService

router = APIRouter(tags=['Workflow'])

@router.post("/issues/{issue_id}/transitions", response_model=TransitionResponse)
async def transition_issue(
    issue_id: int, 
    payload: TransitionRequest,
    x_user_id: int =Header(..., alias='X-User-Id'),
    session: AsyncSession = Depends(get_session)
):
    return await IssuesService.transition(issue_id, payload, x_user_id, session)