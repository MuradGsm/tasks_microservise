from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.managers.dependencies import manager

router = APIRouter()

@router.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket) -> None:
    user_id_raw = websocket.query_params.get("user_id")

    if not user_id_raw:
        await websocket.close(code=1008)
        return
    
    try:
        user_id = int(user_id_raw)
    except ValueError:
        await websocket.close(code=1008)
        return
    
    await manager.connect(user_id, websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)
    except Exception:
        manager.disconnect(user_id, websocket)
        await websocket.close()