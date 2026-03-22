from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_session

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health() -> dict:
    return {
        "status": "ok",
        "service": "notifications-service",
    }


@router.get("/health/live")
async def liveness() -> dict:
    return {
        "status": "ok",
        "service": "notifications-service",
        "check": "live",
    }


@router.get("/health/ready")
async def readiness(session: AsyncSession = Depends(get_session)) -> dict:
    try:
        await session.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "error",
                "service": "notifications-service",
                "check": "ready",
                "database": "down",
            },
        ) from exc

    return {
        "status": "ok",
        "service": "notifications-service",
        "check": "ready",
        "database": "up",
    }