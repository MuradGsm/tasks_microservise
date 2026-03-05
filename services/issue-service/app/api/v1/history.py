from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_session
from app.schemas.history import HistoryOut
from app.services.history_service import HistoryService

router = APIRouter(tags=["History"])


@router.get("/issues/{issue_id}/history", response_model=list[HistoryOut])
async def list_history(
    issue_id: int,
    x_user_id: int = Header(..., alias="X-User-Id"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
):
    return await HistoryService.list(issue_id, x_user_id, session, limit=limit, offset=offset)