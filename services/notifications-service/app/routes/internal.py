from fastapi import APIRouter

from app.managers.dependencies import manager
from app.schemas.notification import NotificationPushRequest

router = APIRouter(prefix='/internal', tags=['Internal'])

@router.post('/notifications/push')
async def push_notification(request: NotificationPushRequest) -> dict:
    await manager.send_to_user(request.user_id, request.payload)

    return {
        "status": "ok",
        "delivered_to": request.user_id,
    }