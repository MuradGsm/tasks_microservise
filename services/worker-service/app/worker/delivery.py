import asyncio

from app.clients.notifications_client import push_notification
from app.config import settings


async def send_notification_with_retry(user_id: int, payload: dict) -> None:
    attempts = settings.NOTIFICATION_RETRY_ATTEMPTS
    base_delay = settings.NOTIFICATION_RETRY_DELAY_SECONDS

    last_error: Exception | None = None

    for attempt in range(1, attempts+1):
        try:
            await push_notification(user_id=user_id, payload=payload)
            return
        except Exception as e:
            last_error = e
            print(
                f"Notification delivery failed for user_id={user_id}, "
                f"attempt={attempt}/{attempts}, error={e}"
            )

            if attempt < attempts:
                delay = base_delay * attempt
                await asyncio.sleep(delay)
    raise RuntimeError(
        f"Notification delivery failed after {attempts} attempts "
        f"for user_id={user_id}: {last_error}"
    )