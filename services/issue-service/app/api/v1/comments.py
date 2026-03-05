from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_session
from app.schemas.comment import CommentOut, CommentCreate
from app.services.comments_service import CommentService


router = APIRouter(tags=["Comments"])


@router.post("/issues/{issue_id}/comments", response_model=CommentOut, status_code=201)
async def create_comment(
    issue_id: int,
    payload: CommentCreate,
    x_user_id: int = Header(..., alias="X-User-Id"),
    session: AsyncSession = Depends(get_session)
):
    return await CommentService.create(issue_id, payload, x_user_id, session)

@router.get("/issues/{issue_id}/comments", response_model=list[CommentOut])
async def list_comments(
    issue_id: int,
    x_user_id: int = Header(..., alias="X-User-Id"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
):
    return await CommentService.list(issue_id, x_user_id, session, limit=limit, offset=offset)