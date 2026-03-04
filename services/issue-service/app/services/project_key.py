from fastapi import  HTTPException
import httpx

from app.config.config import setting

PROJECT_TIMEOUT = 3.0


async def get_project_key(project_id: int, user_id: int) -> str:
    url = f"{setting.PROJECT_SERVICE_URL.rstrip('/')}/v1/projects/{project_id}"

    try:
        async with httpx.AsyncClient(timeout=PROJECT_TIMEOUT) as client:
            resp = await client.get(url, headers={"X-User-Id": str(user_id)})

        if resp.status_code == 200:
            data = resp.json()
            project_key = data.get("key")
            if not project_key:
                raise HTTPException(
                    status_code=502,
                    detail="Project service returned invalid response (no key)",
                )
            return project_key

        if resp.status_code in (403, 404):
            raise HTTPException(
                status_code=resp.status_code,
                detail="Project not found or access denied",
            )

        raise HTTPException(status_code=502, detail="Project service unavailable")

    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Project service unavailable")