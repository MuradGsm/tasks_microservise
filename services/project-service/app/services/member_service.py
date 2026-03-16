from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas.member import ProjectMemberCreate, ProjectMemberOut
from app.services.project_service import get_project
from app.models.project import ProjectMember, Project
from app.core.logging import get_logger

logger = get_logger("app.services.member_service")


async def add_memeber(
    session: AsyncSession, *, project_id: int, owner_id: int, payload: ProjectMemberCreate
) -> ProjectMemberOut:

    logger.info(
        "Project member add requested",
        extra={
            "project_id": project_id,
            "user_id": owner_id,
        },
    )

    project = await get_project(session, project_id=project_id, owner_id=owner_id)

    if payload.user_id == project.owner_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Owner is already part of the project",
        )

    result = await session.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == payload.user_id,
        )
    )

    existing_member = result.scalar_one_or_none()

    if existing_member is not None:

        logger.warning(
            "Project member already exists",
            extra={
                "project_id": project_id,
                "user_id": payload.user_id,
            },
        )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is already a member of this project",
        )

    member = ProjectMember(
        project_id=project_id,
        user_id=payload.user_id,
        role=payload.role,
    )

    session.add(member)
    await session.commit()
    await session.refresh(member)

    logger.info(
        "Project member added",
        extra={
            "project_id": project_id,
            "member_id": member.id,
            "user_id": payload.user_id,
        },
    )

    return member


async def list_member(
    session: AsyncSession, *, project_id: int, owner_id: int
) -> list[ProjectMemberOut]:

    await get_project(session, project_id=project_id, owner_id=owner_id)

    result = await session.execute(
        select(ProjectMember).where(ProjectMember.project_id == project_id)
    )

    members = result.scalars().all()

    logger.info(
        "Project members listed",
        extra={
            "project_id": project_id,
            "user_id": owner_id,
        },
    )

    return members


async def delete_memeber(
    session: AsyncSession, *, project_id: int, owner_id: int, member_id
):

    await get_project(session, project_id=project_id, owner_id=owner_id)

    result = await session.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.id == member_id,
        )
    )

    member = result.scalar_one_or_none()

    if member is None:

        logger.warning(
            "Project member not found",
            extra={
                "project_id": project_id,
                "member_id": member_id,
            },
        )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project member not found!",
        )

    await session.delete(member)
    await session.commit()

    logger.info(
        "Project member removed",
        extra={
            "project_id": project_id,
            "member_id": member_id,
        },
    )


async def has_project_access(
    session: AsyncSession,
    *,
    project_id: int,
    user_id: int,
) -> bool:

    project_result = await session.execute(
        select(Project).where(Project.id == project_id)
    )

    project = project_result.scalar_one_or_none()

    if project is None:

        logger.warning(
            "Project access check failed: project not found",
            extra={
                "project_id": project_id,
                "user_id": user_id,
            },
        )

        return False

    if project.owner_id == user_id:

        logger.info(
            "Project access granted: owner",
            extra={
                "project_id": project_id,
                "user_id": user_id,
            },
        )

        return True

    member_result = await session.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
    )

    member = member_result.scalar_one_or_none()

    if member:

        logger.info(
            "Project access granted: member",
            extra={
                "project_id": project_id,
                "user_id": user_id,
            },
        )

        return True

    logger.info(
        "Project access denied",
        extra={
            "project_id": project_id,
            "user_id": user_id,
        },
    )

    return False