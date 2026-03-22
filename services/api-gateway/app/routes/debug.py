from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/public/ping")
async def public_ping():
    return {"pong": "public"}


@router.get("/private/ping")
async def private_ping(request: Request):
    return {
        "pong": "private",
        "user_id": getattr(request.state, "user_id", None),
    }


@router.get("/private/whoami")
async def whoami(request: Request):
    return {"user_id": getattr(request.state, "user_id", None)}