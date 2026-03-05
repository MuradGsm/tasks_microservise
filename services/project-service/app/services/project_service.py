from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models.project import Project

async def create_project(session: AsyncSession, *, key: str, name: str, owner_id: int) -> Project:
    project = Project(key=key, name=name, owner_id=owner_id)
    session.add(project)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Project key already exists")
    await session.refresh(project)
    return project

async def list_projects(session: AsyncSession, *, owner_id: int) -> list[Project]:
    result = await session.execute(select(Project).where(Project.owner_id == owner_id))
    return result.scalars().all()

async def get_project(session: AsyncSession, *, project_id: int, owner_id: int) -> Project:
    result = await session.execute(
        select(Project).where(Project.id == project_id, Project.owner_id == owner_id)
    )
    project = result.scalar_one_or_none()
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project

async def update_project(session: AsyncSession, *, owner_id: int, project_id: int, name: str) -> Project:
    project = await get_project(session, project_id=project_id, owner_id=owner_id)
    project.name = name
    await session.commit()
    await session.refresh(project)
    return project

async def delete_project(session: AsyncSession, *, owner_id: int, project_id: int) -> None:
    project = await get_project(session, project_id=project_id, owner_id=owner_id)
    await session.delete(project)
    await session.commit()