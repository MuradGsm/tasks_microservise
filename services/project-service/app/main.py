from fastapi import FastAPI, Depends, HTTPException, status, Body, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from app.config.database import get_session, engine, Base
from app.models.project import Project

app = FastAPI(title="SJira API Project Service")

@app.get("/health")
async def health():
    return {"status": "ok", "service": "project-service"}


@app.get('/health/db')
async def health_db(session: AsyncSession = Depends(get_session)):
    try:
        await session.execute(text("SELECT 1"))
        return {"status": "ok", "service": "project-service DB"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {e}")


@app.on_event('startup')
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.post("/v1/projects")
async def create_project(
    key: str = Body(...),
    name: str =Body(...),
    x_user_id: int = Header(..., alias='X-User-Id'),
    session: AsyncSession = Depends(get_session)
):
    project = Project(
        key=key, name=name, owner_id=x_user_id
    )
    session.add(project)
    await session.commit()
    await session.refresh(project)
    return {
        "id": project.id,
        "key": project.key,
        "name": project.name,
        "owner_id": project.owner_id
    }


@app.get('/v1/projects')
async def get_projects(
    x_user_id: int = Header(..., alias='X-User-Id'),
    session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Project).where(Project.owner_id == x_user_id))
    projects = result.scalars().all()
    return [{
        "id": p.id,
        "key": p.key,
        "name": p.name,
        "owner_id": p.owner_id
    } for p in projects]
