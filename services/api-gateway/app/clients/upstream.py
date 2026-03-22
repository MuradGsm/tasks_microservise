import httpx

from app.config import settings

_http_client: httpx.AsyncClient | None = None


async def startup_http_client() -> None:
    global _http_client
    if _http_client is None:
        _http_client = httpx.AsyncClient(timeout=settings.UPSTREAM_TIMEOUT_SECONDS)


async def shutdown_http_client() -> None:
    global _http_client
    if _http_client is not None:
        await _http_client.aclose()
        _http_client = None


def get_http_client() -> httpx.AsyncClient:
    if _http_client is None:
        raise RuntimeError("HTTP client is not initialized")
    return _http_client