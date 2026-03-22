from collections import defaultdict

from fastapi import WebSocket

from app.core.logging import get_logger
from app.core.metrics import (
    websocket_active_connections,
    websocket_delivery_failed_total,
    websocket_delivery_skipped_total,
    websocket_messages_sent_total,
)

logger = get_logger("app.managers.connection_manager")


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: dict[int, list[WebSocket]] = defaultdict(list)

    async def connect(self, user_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections[user_id].append(websocket)
        websocket_active_connections.inc()

        logger.info(
            "WebSocket user connected",
            extra={
                "user_id": user_id,
                "connection_count": len(self.active_connections[user_id]),
            },
        )

    def disconnect(self, user_id: int, websocket: WebSocket) -> None:
        connections = self.active_connections.get(user_id, [])

        if websocket in connections:
            connections.remove(websocket)
            websocket_active_connections.dec()

        current_connections = len(connections)

        if current_connections == 0 and user_id in self.active_connections:
            del self.active_connections[user_id]

        logger.info(
            "WebSocket user disconnected",
            extra={
                "user_id": user_id,
                "connection_count": current_connections,
            },
        )

    async def send_to_user(self, user_id: int, payload: dict) -> None:
        connections = self.active_connections.get(user_id, [])
        notification_type = payload.get("type", "unknown")

        if not connections:
            websocket_delivery_skipped_total.labels(type=notification_type).inc()

            logger.info(
                "Realtime delivery skipped: no active connections",
                extra={
                    "user_id": user_id,
                    "notification_id": payload.get("id"),
                    "notification_type": notification_type,
                    "delivery_status": "skipped",
                    "connection_count": 0,
                },
            )
            return

        dead_connections: list[WebSocket] = []

        for websocket in connections:
            try:
                await websocket.send_json(payload)
                websocket_messages_sent_total.labels(type=notification_type).inc()

                logger.info(
                    "Notification delivered realtime",
                    extra={
                        "user_id": user_id,
                        "notification_id": payload.get("id"),
                        "notification_type": notification_type,
                        "project_id": payload.get("project_id"),
                        "entity_id": payload.get("entity_id"),
                        "entity_type": payload.get("entity_type"),
                        "delivery_status": "sent",
                    },
                )
            except Exception:
                websocket_delivery_failed_total.labels(type=notification_type).inc()

                logger.exception(
                    "Realtime delivery failed",
                    extra={
                        "user_id": user_id,
                        "notification_id": payload.get("id"),
                        "notification_type": notification_type,
                        "delivery_status": "failed",
                    },
                )
                dead_connections.append(websocket)

        for websocket in dead_connections:
            self.disconnect(user_id, websocket)