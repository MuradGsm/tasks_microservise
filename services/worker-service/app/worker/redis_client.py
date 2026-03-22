import redis.asyncio as redis

from app.config import settings


redis_client = redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
)


async def ping_redis() -> bool:
    return bool(await redis_client.ping())


async def close_redis() -> None:
    await redis_client.aclose()