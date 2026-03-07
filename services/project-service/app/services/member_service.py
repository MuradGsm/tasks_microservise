from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas.member import ProjectMemberCreate, ProjectMemberOut
from app.services.project_service import get_project
from app.models.project import ProjectMember, Project

async def add_memeber(
    session: AsyncSession, *, project_id: int, owner_id: int, payload: ProjectMemberCreate
) -> ProjectMemberOut:
    project = await get_project(session, project_id=project_id, owner_id=owner_id)

    if payload.user_id == project.owner_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Owner is already part of the project")
    
    result = await session.execute(select(ProjectMember).where(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == payload.user_id
    ))

    existing_member = result.scalar_one_or_none()
    if existing_member is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User is alerady a member of this project")
    
    member = ProjectMember(
        project_id=project_id,
        user_id=payload.user_id,
        role=payload.role
    )

    session.add(member)
    await session.commit()
    await session.refresh(member)

    return member


async def list_member(session: AsyncSession, *, project_id: int, owner_id: int) -> list[ProjectMemberOut]:
    await get_project(session, project_id=project_id, owner_id=owner_id)
    result = await session.execute(select(ProjectMember).where(ProjectMember.project_id == project_id))

    return result.scalars().all()

async def delete_memeber(session: AsyncSession, *, project_id: int, owner_id: int, member_id):
    await get_project(session, project_id=project_id, owner_id=owner_id)

    result = await session.execute(select(ProjectMember).where(
        ProjectMember.project_id == project_id,
        ProjectMember.id == member_id
    ))
    
    member = result.scalar_one_or_none()

    if member is None: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Project memeber not found!')
    
    await session.delete(member)
    await session.commit()

async def has_project_access(
    session: AsyncSession,
    *,
    project_id: int,
    user_id: int
) -> bool:
    project_result = await session.execute(select(Project).where(Project.id == project_id))

    project = project_result.scalar_one_or_none()

    if project is None:
        return False
    
    if project.owner_id == user_id:
        return True
    
    member_result = await session.execute(select(ProjectMember).where(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id
    ))

    memeber = member_result.scalar_one_or_none()

    return memeber is not None