from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.schemas.notification import NotificationCreate


class NotificationsService:
    @staticmethod
    async def create_notification(
        data: NotificationCreate,
        session: AsyncSession,
    ) -> Notification:
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

        return notification

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

        return list(items), total

    @staticmethod
    async def unread_count(user_id: int, session: AsyncSession) -> int:
        stmt = select(func.count()).select_from(Notification).where(
            Notification.user_id == user_id,
            Notification.is_read.is_(False),
        )
        count = await session.scalar(stmt)
        return count or 0

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
            return None

        if not notification.is_read:
            notification.is_read = True
            await session.commit()
            await session.refresh(notification)

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

        return result.rowcount or 0