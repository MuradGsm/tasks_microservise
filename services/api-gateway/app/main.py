from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uuid
import os
import httpx

app = FastAPI(title="SJira API Gateway")

IDENTITY_URL = os.getenv("IDENTITY_URL", "http://identity-service:8000")
PROJECT_URL = os.getenv("PROJECT_URL", "http://project-service:8000")
ISSUE_URL = os.getenv("ISSUE_URL", "http://issue-service:8000")


# 1) Request-ID всегда добавляем первым
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


# 2) Auth middleware
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    public_paths = {"/health", "/public/ping"}
    if request.url.path in public_paths:
        return await call_next(request)

    public_prefixes = ("/docs", "/openapi.json", "/redoc")
    if request.url.path in public_paths or request.url.path.startswith(public_prefixes):
        return await call_next(request)

    auth_header = request.headers.get("authorization", "")
    if not auth_header.lower().startswith("bearer "):
        return JSONResponse({"detail": "Missing Bearer token"}, status_code=401)

    token = auth_header.split(" ", 1)[1].strip()

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                f"{IDENTITY_URL}/auth/me/",
                headers={"Authorization": f"Bearer {token}"},
            )
    except httpx.RequestError:
        return JSONResponse({"detail": "Identity service unavailable"}, status_code=503)

    if resp.status_code != 200:
        # отладка: покажем, что вернул identity
        return JSONResponse(
            {"detail": "Invalid token", "identity_status": resp.status_code, "identity_body": resp.text},
            status_code=401,
        )

    data = resp.json()
    user_id = data.get("id") or data.get("user_id")
    if user_id is None:
        return JSONResponse({"detail": "Identity response missing user id"}, status_code=500)

    request.state.user_id = str(user_id)

    return await call_next(request)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "api-gateway"}

@app.get("/public/ping")
async def public_ping():
    return {"pong": "public"}

@app.get("/private/ping")
async def private_ping():
    return {"pong": "private"}

@app.api_route('/projects/{path:path}', methods=['GET','POST', 'PUT', "PATCH", "DELETE"])
async def proxy_projects(request: Request, path: str):
    upstream_url = f'{PROJECT_URL}/{path}'

    body = await request.body()

    headers = {}

    if request.headers.get('content-type'):
        headers['content-type'] = request.headers['content-type']
    
    headers['X-User-Id'] = getattr(request.state, 'user_id', '')

    async with httpx.AsyncClient(timeout=10.0) as client:
        upstream_resp = await client.request(
            method=request.method,
            url=upstream_url,
            params=request.query_params,
            content=body,
            headers=headers,
        )

    return Response(
        content=upstream_resp.content,
        status_code=upstream_resp.status_code,
        media_type=upstream_resp.headers.get("content-type")
    )

@app.get("/private/whoami")
async def whoami(request: Request):
    return {"user_id": getattr(request.state, "user_id", None)}


@app.api_route("/issues/{path:path}", methods=["GET","POST","PUT","PATCH","DELETE"])
async def proxy_issues(request: Request, path: str):
    upstream_url = f"{ISSUE_URL}/{path}"
    body = await request.body()
    headers = {}
    if request.headers.get("content-type"):
        headers["content-type"] = request.headers["content-type"]
    headers["X-User-Id"] = getattr(request.state, "user_id", "")
    async with httpx.AsyncClient(timeout=10.0) as client:
        upstream_resp = await client.request(
            method=request.method,
            url=upstream_url,
            params=request.query_params,
            content=body,
            headers=headers,
        )
    return Response(
        content=upstream_resp.content,
        status_code=upstream_resp.status_code,
        media_type=upstream_resp.headers.get("content-type"),
    )