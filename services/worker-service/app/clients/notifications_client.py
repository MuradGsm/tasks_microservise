import httpx

from app.config import settings

NOTIFICATIONS_TIMEOUT = 3.0


async def push_notification(user_id: int, payload: dict) -> None:
    url = f"{settings.NOTIFICATIONS_URL.rstrip('/')}/internal/notifications/push"

    body = {
        "user_id": user_id,
        "payload": payload,
    }

    try:
        async with httpx.AsyncClient(timeout=NOTIFICATIONS_TIMEOUT) as client:
            response = await client.post(url, json=body)

        if response.status_code != 200:
            raise RuntimeError(
                f"Notifications service error: {response.status_code} {response.text}"
            )

    except httpx.RequestError as e:
        raise RuntimeError(f"Notifications service unavailable: {e}")