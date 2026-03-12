from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_session
from app.managers.dependencies import manager
from app.schemas.notification import NotificationCreate, NotificationPushRequest
from app.services.notifications_service import NotificationsService

router = APIRouter(prefix="/internal", tags=["Internal"])


@router.post("/notifications/push")
async def push_notification(
    request: NotificationPushRequest,
    session: AsyncSession = Depends(get_session),
) -> dict:
    notification = await NotificationsService.create_notification(
        NotificationCreate(
            user_id=request.user_id,
            type=request.payload.type,
            title=request.payload.title,
            message=request.payload.message,
            entity_type=request.payload.entity_type,
            entity_id=request.payload.entity_id,
            project_id=request.payload.project_id,
        ),
        session,
    )

    await manager.send_to_user(
        request.user_id,
        {
            "id": notification.id,
            "user_id": notification.user_id,
            "type": notification.type,
            "title": notification.title,
            "message": notification.message,
            "entity_type": notification.entity_type,
            "entity_id": notification.entity_id,
            "project_id": notification.project_id,
            "is_read": notification.is_read,
            "created_at": notification.created_at.isoformat(),
        },
    )

    return {
        "status": "ok",
        "notification_id": notification.id,
        "delivered_to": request.user_id,
    }