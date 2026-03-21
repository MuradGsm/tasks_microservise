from fastapi import Depends, Header, APIRouter, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_session
from app.schemas.member import ProjectMemberCreate, ProjectMemberOut, ProjectAccessOut
from app.services import member_service

router = APIRouter()

@router.post('/{project_id}/members')
async def create_member(
    project_id: int, 
    payload: ProjectMemberCreate,
    x_user_id: int = Header(..., alias='X-User-Id'),
    session: AsyncSession = Depends(get_session)
):
    member = await member_service.add_member(session, project_id=project_id, owner_id=x_user_id, payload=payload)

    return ProjectMemberOut(
        id = member.id,
        project_id=member.project_id,
        user_id=member.user_id,
        role=member.role
    )

@router.get('/{project_id}/members')
async def list_members(
    project_id: int, 
    x_user_id: int = Header(..., alias='X-User-Id'),
    session: AsyncSession = Depends(get_session)
):
    members = await member_service.list_members(session, project_id=project_id, owner_id=x_user_id)

    return [
        ProjectMemberOut(
            id = m.id,
        project_id=m.project_id,
        user_id=m.user_id,
        role=m.role
        ) for m in members
    ]


@router.delete('/{project_id}/members/{member_id}', status_code=204)
async def delete_member(
    project_id: int,
    member_id: int,
    x_user_id: int = Header(..., alias="X-User-Id"),
    session: AsyncSession = Depends(get_session),
):
    await member_service.delete_member(
        session,
        project_id=project_id,
        member_id=member_id,
        owner_id=x_user_id,
    )
    return Response(status_code=204)

@router.get("/{project_id}/access/{user_id}", response_model=ProjectAccessOut)
async def check_project_access(
    project_id: int,
    user_id: int,
    session: AsyncSession = Depends(get_session)
):
    has_access = await member_service.has_project_access(session, project_id=project_id, user_id=user_id)
    return ProjectAccessOut(has_access=has_access)