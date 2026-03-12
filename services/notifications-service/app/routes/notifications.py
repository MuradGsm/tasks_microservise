from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_session
from app.schemas.notification import (
    NotificationListResponse,
    NotificationRead,
    UnreadCountResponse,
)
from app.services.notifications_service import NotificationsService

router = APIRouter(prefix="/v1/notifications", tags=["Notifications"])


def get_current_user_id(x_user_id: int = Header(..., alias="X-User-Id")) -> int:
    return x_user_id


@router.get("", response_model=NotificationListResponse)
async def list_notifications(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
):
    items, total = await NotificationsService.list_notifications(
        user_id=user_id,
        session=session,
        limit=limit,
        offset=offset,
    )

    return {
        "items": items,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/unread-count", response_model=UnreadCountResponse)
async def get_unread_count(
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
):
    unread_count = await NotificationsService.unread_count(user_id, session)
    return {"unread_count": unread_count}


@router.post("/{notification_id}/read", response_model=NotificationRead)
async def mark_notification_as_read(
    notification_id: int,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
):
    notification = await NotificationsService.mark_as_read(
        notification_id=notification_id,
        user_id=user_id,
        session=session,
    )

    if notification is None:
        raise HTTPException(status_code=404, detail="Notification not found")

    return notification


@router.post("/read-all")
async def mark_all_notifications_as_read(
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
):
    updated = await NotificationsService.mark_all_as_read(
        user_id=user_id,
        session=session,
    )

    return {
        "status": "ok",
        "updated": updated,
    }