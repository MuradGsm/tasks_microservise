from fastapi import APIRouter, Depends, Header, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_session
from app.schemas.project import ProjectCreate, ProjectOut, ProjectUpdate
from app.services import project_service

router = APIRouter()

@router.post("", response_model=ProjectOut, status_code=201)
async def create_project(
    payload: ProjectCreate,
    x_user_id: int = Header(..., alias='X-User-Id'),
    session: AsyncSession = Depends(get_session)
):
    p = await project_service.create_project(session, key=payload.key, name=payload.name, owner_id=x_user_id)
    return ProjectOut(id = p.id, key=p.key, name=p.name, owner_id=p.owner_id)

@router.get("", response_model=list[ProjectOut])
async def list_projects(
    x_user_id: int = Header(..., alias="X-User-Id"),
    session: AsyncSession = Depends(get_session),
):
    projects = await project_service.list_projects(session, owner_id=x_user_id)
    return [ProjectOut(id=p.id, key=p.key, name=p.name, owner_id=p.owner_id) for p in projects]

@router.get("/{project_id}", response_model=ProjectOut)
async def get_project(
    project_id: int,
    x_user_id: int = Header(..., alias="X-User-Id"),
    session: AsyncSession = Depends(get_session),
):
    p = await project_service.get_project(session, project_id=project_id, owner_id=x_user_id)
    return ProjectOut(id=p.id, key=p.key, name=p.name, owner_id=p.owner_id)

@router.patch("/{project_id}", response_model=ProjectOut)
async def update_project(
    project_id: int,
    data: ProjectUpdate,
    x_user_id: int = Header(..., alias="X-User-Id"),
    session: AsyncSession = Depends(get_session),
):
    p = await project_service.update_project(session, owner_id=x_user_id, project_id=project_id, name=data.name)
    return ProjectOut(id=p.id, key=p.key, name=p.name, owner_id=p.owner_id)

@router.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: int,
    x_user_id: int = Header(..., alias="X-User-Id"),
    session: AsyncSession = Depends(get_session),
):
    await project_service.delete_project(session, project_id=project_id, owner_id=x_user_id)
    return Response(status_code=204)