from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.logging import get_logger
from app.managers.dependencies import manager

router = APIRouter()
logger = get_logger("app.routes.websocket")


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    user_id_raw = websocket.query_params.get("user_id")

    if not user_id_raw:
        logger.info("WebSocket rejected: missing user_id")
        await websocket.close(code=1008)
        return

    try:
        user_id = int(user_id_raw)
    except ValueError:
        logger.info("WebSocket rejected: invalid user_id")
        await websocket.close(code=1008)
        return

    await manager.connect(user_id, websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        logger.info(
            "WebSocket client disconnected",
            extra={
                "user_id": user_id,
            },
        )
        manager.disconnect(user_id, websocket)
    except Exception:
        logger.exception(
            "WebSocket connection failed",
            extra={
                "user_id": user_id,
            },
        )
        manager.disconnect(user_id, websocket)
        await websocket.close()