from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.core.metrics import (
    notifications_created_total,
    notifications_deduplicated_total,
    notifications_mark_all_read_total,
    notifications_marked_read_total,
)
from app.models.notification import Notification
from app.schemas.notification import NotificationCreate

logger = get_logger("app.services.notifications_service")


class NotificationsService:
    @staticmethod
    async def create_notification(
        data: NotificationCreate,
        session: AsyncSession,
    ) -> tuple[Notification, bool]:
        dedup_since = datetime.now(timezone.utc) - timedelta(minutes=5)

        stmt = (
            select(Notification)
            .where(
                Notification.user_id == data.user_id,
                Notification.type == data.type,
                Notification.entity_type == data.entity_type,
                Notification.entity_id == data.entity_id,
                Notification.project_id == data.project_id,
                Notification.is_read.is_(False),
                Notification.created_at >= dedup_since,
            )
            .order_by(Notification.created_at.desc(), Notification.id.desc())
        )

        result = await session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing is not None:
            notifications_deduplicated_total.labels(type=data.type).inc()

            logger.info(
                "Notification deduplicated",
                extra={
                    "user_id": data.user_id,
                    "notification_id": existing.id,
                    "notification_type": data.type,
                    "project_id": data.project_id,
                    "entity_id": data.entity_id,
                    "entity_type": data.entity_type,
                    "notification_created": False,
                },
            )
            return existing, False

        notification = Notification(
            user_id=data.user_id,
            type=data.type,
            title=data.title,
            message=data.message,
            entity_type=data.entity_type,
            entity_id=data.entity_id,
            project_id=data.project_id,
            is_read=False,
        )
        session.add(notification)
        await session.commit()
        await session.refresh(notification)

        notifications_created_total.labels(type=data.type).inc()

        logger.info(
            "Notification persisted",
            extra={
                "user_id": notification.user_id,
                "notification_id": notification.id,
                "notification_type": notification.type,
                "project_id": notification.project_id,
                "entity_id": notification.entity_id,
                "entity_type": notification.entity_type,
                "notification_created": True,
                "is_read": notification.is_read,
            },
        )
        return notification, True

    @staticmethod
    async def list_notifications(
        user_id: int,
        session: AsyncSession,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Notification], int]:
        total_stmt = select(func.count()).select_from(Notification).where(
            Notification.user_id == user_id
        )
        total = await session.scalar(total_stmt)
        total = total or 0

        stmt = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc(), Notification.id.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await session.execute(stmt)
        items = result.scalars().all()

        logger.info(
            "Notifications listed",
            extra={
                "user_id": user_id,
                "limit": limit,
                "offset": offset,
                "total": total,
            },
        )
        return list(items), total

    @staticmethod
    async def unread_count(user_id: int, session: AsyncSession) -> int:
        stmt = select(func.count()).select_from(Notification).where(
            Notification.user_id == user_id,
            Notification.is_read.is_(False),
        )
        count = await session.scalar(stmt)
        count = count or 0

        logger.info(
            "Unread notifications counted",
            extra={
                "user_id": user_id,
                "unread_count": count,
            },
        )
        return count

    @staticmethod
    async def mark_as_read(
        notification_id: int,
        user_id: int,
        session: AsyncSession,
    ) -> Notification | None:
        stmt = select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user_id,
        )
        result = await session.execute(stmt)
        notification = result.scalar_one_or_none()

        if notification is None:
            logger.info(
                "Notification not found for mark_as_read",
                extra={
                    "user_id": user_id,
                    "notification_id": notification_id,
                },
            )
            return None

        if not notification.is_read:
            notification.is_read = True
            await session.commit()
            await session.refresh(notification)
            notifications_marked_read_total.inc()

            logger.info(
                "Notification marked as read",
                extra={
                    "user_id": user_id,
                    "notification_id": notification.id,
                    "notification_type": notification.type,
                    "is_read": notification.is_read,
                },
            )
            return notification

        logger.info(
            "Notification already marked as read",
            extra={
                "user_id": user_id,
                "notification_id": notification.id,
                "notification_type": notification.type,
                "is_read": notification.is_read,
            },
        )
        return notification

    @staticmethod
    async def mark_all_as_read(
        user_id: int,
        session: AsyncSession,
    ) -> int:
        stmt = (
            update(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.is_read.is_(False),
            )
            .values(is_read=True)
        )

        result = await session.execute(stmt)
        await session.commit()
        updated = result.rowcount or 0

        if updated > 0:
            notifications_mark_all_read_total.inc(updated)

        logger.info(
            "All notifications marked as read",
            extra={
                "user_id": user_id,
                "updated_count": updated,
            },
        )
        return updated