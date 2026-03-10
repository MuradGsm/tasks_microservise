import httpx

from app.config import settings

NOTIFICATION_TIMEOUT = 3.0

async def push_notification(user_id: int, payload: dict) -> None:
    url = f"{settings.NOTIFICATIONS_URL.rstrip('/')}/internal/notifications/push"

    body = {
        "user_id": user_id,
        "payload": payload
    }

    try:
        async with httpx.AsyncClient(timeout=NOTIFICATION_TIMEOUT) as client:
            response = await client.post(url, json=body)

        if response.status_code != 200:
            print(
                "Failed to push notification:",
                response.status_code,
                response.text,                
            )
    except httpx.RequestError as e:
        print(f"Notifications service unavailable: {e}")