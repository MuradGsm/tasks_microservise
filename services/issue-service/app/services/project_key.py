from fastapi import  HTTPException
import httpx

from app.config.settings import settings
from app.core.logging import get_logger

from app.core.metrics import (
    project_service_requests_total,
    project_service_request_failures_total,
)

logger = get_logger(__name__)

PROJECT_TIMEOUT = 3.0


async def get_project_key(project_id: int, user_id: int) -> str:
    url = f"{settings.PROJECT_SERVICE_URL.rstrip('/')}/v1/projects/{project_id}"

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

            project_service_requests_total.labels(
                operation="get_project_key",
                status="success",
            ).inc()

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
            project_service_requests_total.labels(
                operation="get_project_key",
                status="denied_or_not_found",
            ).inc()
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
        project_service_requests_total.labels(
            operation="get_project_key",
            status="bad_response",
        ).inc()
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
        project_service_request_failures_total.labels(
            operation="get_project_key",
        ).inc()
        raise HTTPException(status_code=502, detail="Project service unavailable")

async def check_project_access(project_id: int, user_id: int) -> bool:
    url = f"{settings.PROJECT_SERVICE_URL.rstrip('/')}/v1/projects/{project_id}/access/{user_id}"
    logger.info(
        "Checking project access in project-service",
        extra={
            "project_id": project_id,
            "user_id": user_id,
            "target_service": "project-service",
            "url": url,
        },
    )
    try:
        async with httpx.AsyncClient(timeout=PROJECT_TIMEOUT) as client:
            resp = await client.get(url)
        
        if resp.status_code == 200:
            data = resp.json()
            project_service_requests_total.labels(
                operation="check_project_access",
                status="success",
            ).inc()
            logger.info(
                "Project access check success",
                extra={
                    "project_id": project_id,
                    "user_id": user_id,
                    "status_code": resp.status_code,
                    "target_service": "project-service",
                },
            )
            return bool(data.get('has_access', False))
        project_service_requests_total.labels(
            operation="check_project_access",
            status="bad_response",
        ).inc()
        logger.warning(
            "Project access check failed with bad response",
            extra={
                "project_id": project_id,
                "user_id": user_id,
                "status_code": resp.status_code,
                "target_service": "project-service",
            },
        )
        raise HTTPException(status_code=502, detail="Project service unavailable")
    
    except httpx.RequestError:
        project_service_request_failures_total.labels(
            operation="check_project_access",
        ).inc()
        logger.exception(
            "Project-service access check request failed",
            extra={
                "project_id": project_id,
                "user_id": user_id,
                "url": url,
                "target_service": "project-service",
            },
        )
        raise HTTPException(status_code=502, detail="Project service unavailable")