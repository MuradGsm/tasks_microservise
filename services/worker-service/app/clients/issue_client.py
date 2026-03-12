import httpx

from app.config import settings

ISSUE_TIMEOUT = 3.0


async def get_issue(issue_id: int) -> dict:
    url = f"{settings.ISSUE_URL.rstrip('/')}/internal/issues/{issue_id}"

    try:
        async with httpx.AsyncClient(timeout=ISSUE_TIMEOUT) as client:
            response = await client.get(url)

        if response.status_code != 200:
            raise RuntimeError(
                f"Issue service error: {response.status_code} {response.text}"
            )

        return response.json()

    except httpx.RequestError as e:
        raise RuntimeError(f"Issue service unavailable: {e}")