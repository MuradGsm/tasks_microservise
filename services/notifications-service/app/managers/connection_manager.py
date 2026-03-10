from collections import defaultdict
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: dict[int, list[WebSocket]] = defaultdict(list)

    async def connect(self, user_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections[user_id].append(websocket)

        print(
            f"User {user_id} connected. "
            f"Active connections: {len(self.active_connections[user_id])}"
        )
    
    def disconnect(self, user_id: int, websocket: WebSocket) -> None:
        connections = self.active_connections.get(user_id, [])

        if websocket in connections:
            connections.remove(websocket)
        
        if not connections and user_id in self.active_connections:
            del self.active_connections[user_id]
        
        print(
            f"User {user_id} disconnected. "
            f"Remaining connections: {len(self.active_connections.get(user_id, []))}"
        )
    
    async def send_to_user(self, user_id: int, payload: dict) -> None:
        connections = self.active_connections.get(user_id, [])

        if not connections:
            print(f"No active connections for user {user_id}")
            return
        
        dead_connections: list[WebSocket] = []

        for websocket in connections:
            try:
                await websocket.send_json(payload)
            except Exception as e:
                print(f"Failed to send notification to user {user_id}: {e}")
                dead_connections.append(websocket)
            
        for websocket in dead_connections:
            self.disconnect(user_id, websocket)