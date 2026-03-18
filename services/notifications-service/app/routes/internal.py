import time

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.core.metrics import (
    notification_delivery_duration_seconds,
    notifications_push_failed_total,
    notifications_push_total,
)
from app.db.database import get_session
from app.managers.dependencies import manager
from app.schemas.notification import NotificationCreate, NotificationPushRequest
from app.services.notifications_service import NotificationsService

router = APIRouter(prefix="/internal", tags=["Internal"])
logger = get_logger("app.routes.internal")


@router.post("/notifications/push")
async def push_notification(
    request: NotificationPushRequest,
    session: AsyncSession = Depends(get_session),
) -> dict:
    notification_type = request.payload.type
    notifications_push_total.labels(type=notification_type).inc()
    started = time.perf_counter()

    try:
        logger.info(
            "Push notification request received",
            extra={
                "user_id": request.user_id,
                "project_id": request.payload.project_id,
                "entity_id": request.payload.entity_id,
                "entity_type": request.payload.entity_type,
            },
        )

        logger.info(
            "Push notification payload validated",
            extra={
                "user_id": request.user_id,
                "project_id": request.payload.project_id,
                "entity_id": request.payload.entity_id,
                "entity_type": request.payload.entity_type,
            },
        )

        notification, created = await NotificationsService.create_notification(
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

        if created:
            logger.info(
                "Realtime delivery attempted",
                extra={
                    "user_id": request.user_id,
                    "notification_id": notification.id,
                    "project_id": notification.project_id,
                    "entity_id": notification.entity_id,
                    "entity_type": notification.entity_type,
                    "delivered_to": request.user_id,
                },
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

        duration = time.perf_counter() - started
        notification_delivery_duration_seconds.labels(
            type=notification_type
        ).observe(duration)

        logger.info(
            "Push notification request processed successfully",
            extra={
                "user_id": request.user_id,
                "notification_id": notification.id,
                "project_id": notification.project_id,
                "entity_id": notification.entity_id,
                "entity_type": notification.entity_type,
                "duration_ms": round(duration * 1000, 2),
            },
        )

        return {
            "status": "ok",
            "notification_id": notification.id,
            "delivered_to": request.user_id,
            "created": created,
        }

    except Exception:
        duration = time.perf_counter() - started
        notification_delivery_duration_seconds.labels(
            type=notification_type
        ).observe(duration)

        notifications_push_failed_total.labels(type=notification_type).inc()
        logger.exception(
            "Push notification request failed",
            extra={
                "user_id": request.user_id,
                "project_id": request.payload.project_id,
                "entity_id": request.payload.entity_id,
                "entity_type": request.payload.entity_type,
                "duration_ms": round(duration * 1000, 2),
            },
        )
        raise