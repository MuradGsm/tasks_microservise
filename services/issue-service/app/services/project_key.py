from fastapi import  HTTPException
import httpx

from app.config.config import setting
from app.core.logging import get_logger

logger = get_logger(__name__)

PROJECT_TIMEOUT = 3.0


async def get_project_key(project_id: int, user_id: int) -> str:
    url = f"{setting.PROJECT_SERVICE_URL.rstrip('/')}/v1/projects/{project_id}"

    logger.info(
        "Requesting project key from project-service",
        extra={
            "project_id": project_id,
            "user_id": user_id,
            "url": url,
            "target_service": "project-service",
        },
    )

    try:
        async with httpx.AsyncClient(timeout=PROJECT_TIMEOUT) as client:
            resp = await client.get(url, headers={"X-User-Id": str(user_id)})

        if resp.status_code == 200:
            data = resp.json()
            project_key = data.get("key")

            logger.info(
                "Project key received from project-service",
                extra={
                    "project_id": project_id,
                    "user_id": user_id,
                    "status_code": resp.status_code,
                    "target_service": "project-service",
                },
            )

            if not project_key:
                raise HTTPException(
                    status_code=502,
                    detail="Project service returned invalid response (no key)",
                )
            return project_key

        if resp.status_code in (403, 404):
            logger.warning(
                "Project access denied or project not found",
                extra={
                    "project_id": project_id,
                    "user_id": user_id,
                    "status_code": resp.status_code,
                    "target_service": "project-service",
                },
            )
            raise HTTPException(
                status_code=resp.status_code,
                detail="Project not found or access denied",
            )

        logger.warning(
            "Unexpected response from project-service",
            extra={
                "project_id": project_id,
                "user_id": user_id,
                "status_code": resp.status_code,
                "target_service": "project-service",
            },
        )
        raise HTTPException(status_code=502, detail="Project service unavailable")

    except httpx.RequestError:
        logger.exception(
            "Project-service request failed",
            extra={
                "project_id": project_id,
                "user_id": user_id,
                "url": url,
                "target_service": "project-service",
            },
        )
        raise HTTPException(status_code=502, detail="Project service unavailable")

async def check_project_access(project_id: int, user_id: int) -> bool:
    url = f"{setting.PROJECT_SERVICE_URL.rstrip('/')}/v1/projects/{project_id}/access/{user_id}"

    try:
        async with httpx.AsyncClient(timeout=PROJECT_TIMEOUT) as client:
            resp = await client.get(url)
        
        if resp.status_code == 200:
            data = resp.json()
            return bool(data.get('has_access', False))
        
        raise HTTPException(status_code=502, detail="Project service unavailable")
    
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Project service unavailable")