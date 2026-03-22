def make_push_payload(
    user_id: int = 10,
    entity_id: int = 1,
    project_id: int = 1,
    notification_type: str = "issue_created",
):
    return {
        "user_id": user_id,
        "payload": {
            "type": notification_type,
            "title": "New issue",
            "message": f"Issue {entity_id} was created",
            "entity_type": "issue",
            "entity_id": entity_id,
            "project_id": project_id,
        },
    }


def test_websocket_receives_pushed_notification():
    from app.main import app
    from fastapi.testclient import TestClient

    with TestClient(app) as client:
        with client.websocket_connect("/ws?user_id=10") as websocket:
            response = client.post(
                "/internal/notifications/push",
                json=make_push_payload(),
            )

            assert response.status_code == 200
            data = websocket.receive_json()

            assert data["user_id"] == 10
            assert data["type"] == "issue_created"
            assert data["entity_type"] == "issue"
            assert data["entity_id"] == 1
            assert data["project_id"] == 1


def test_websocket_rejects_missing_user_id():
    from app.main import app
    from fastapi.testclient import TestClient
    from starlette.websockets import WebSocketDisconnect

    with TestClient(app) as client:
        try:
            with client.websocket_connect("/ws"):
                pass
        except WebSocketDisconnect as exc:
            assert exc.code == 1008