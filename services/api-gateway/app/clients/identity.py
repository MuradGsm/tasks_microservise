import httpx

from app.clients.upstream import get_http_client
from app.config import settings


PUBLIC_PATHS = {
    "/health",
    "/ready",
    "/metrics",
    "/public/ping",
    "/auth/token/",
    "/auth/token/refresh/",
}

PUBLIC_PREFIXES = ("/docs", "/openapi.json", "/redoc")


def is_public_path(path: str) -> bool:
    return path in PUBLIC_PATHS or path.startswith(PUBLIC_PREFIXES)


async def validate_token(token: str, request_id: str) -> httpx.Response:
    client = get_http_client()
    return await client.get(
        f"{settings.IDENTITY_URL}/auth/me/",
        headers={
            "Authorization": f"Bearer {token}",
            "X-Request-Id": request_id,
        },
        timeout=settings.AUTH_TIMEOUT_SECONDS,
    )


async def check_identity_health(request_id: str) -> httpx.Response:
    client = get_http_client()
    return await client.get(
        f"{settings.IDENTITY_URL}/health",
        headers={"X-Request-Id": request_id},
        timeout=settings.AUTH_TIMEOUT_SECONDS,
    )