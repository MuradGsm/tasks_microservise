from fastapi import APIRouter, Request

from app.config import settings
from app.services.proxy import proxy_request

router = APIRouter()


@router.api_route(
    "/projects/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
)
async def proxy_projects(request: Request, path: str):
    upstream_url = f"{settings.PROJECT_URL}/v1/projects/{path}"
    return await proxy_request(
        request,
        upstream_url,
        upstream_service="project-service",
    )


@router.api_route(
    "/issues/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
)
async def proxy_issues(request: Request, path: str):
    upstream_url = f"{settings.ISSUE_URL}/v1/issues/{path}"
    return await proxy_request(
        request,
        upstream_url,
        upstream_service="issue-service",
    )


@router.api_route("/notifications", methods=["GET"])
@router.api_route(
    "/notifications/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
)
async def proxy_notifications(request: Request, path: str = ""):
    upstream_url = f"{settings.NOTIFICATIONS_URL}/v1/notifications"
    if path:
        upstream_url = f"{upstream_url}/{path}"

    return await proxy_request(
        request,
        upstream_url,
        upstream_service="notifications-service",
    )


@router.api_route("/auth/{path:path}", methods=["GET", "POST"])
async def proxy_auth(request: Request, path: str):
    upstream_url = f"{settings.IDENTITY_URL}/auth/{path}"
    return await proxy_request(
        request,
        upstream_url,
        upstream_service="identity-service",
    )