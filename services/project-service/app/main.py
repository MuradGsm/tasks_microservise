from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.config.database import get_session
from app.api.v1.router import router as project_router

app = FastAPI(title="SJira API Project Service")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "project-service"}


@app.get("/health/db")
async def health_db(session: AsyncSession = Depends(get_session)):
    try:
        await session.execute(text("SELECT 1"))
        return {"status": "ok", "service": "project-service DB"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"DB error: {e}",
        )


app.include_router(project_router, prefix="/v1")