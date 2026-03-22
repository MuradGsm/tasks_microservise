import pytest


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


@pytest.mark.asyncio
async def test_internal_push_creates_notification(client):
    response = await client.post(
        "/internal/notifications/push",
        json=make_push_payload(),
    )

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "ok"
    assert data["delivered_to"] == 10
    assert data["created"] is True
    assert isinstance(data["notification_id"], int)


@pytest.mark.asyncio
async def test_duplicate_push_returns_created_false(client):
    first = await client.post(
        "/internal/notifications/push",
        json=make_push_payload(),
    )
    second = await client.post(
        "/internal/notifications/push",
        json=make_push_payload(),
    )

    assert first.status_code == 200
    assert second.status_code == 200

    first_data = first.json()
    second_data = second.json()

    assert first_data["created"] is True
    assert second_data["created"] is False
    assert second_data["notification_id"] == first_data["notification_id"]


@pytest.mark.asyncio
async def test_list_notifications_returns_items_and_total(client):
    await client.post(
        "/internal/notifications/push",
        json=make_push_payload(entity_id=1),
    )
    await client.post(
        "/internal/notifications/push",
        json=make_push_payload(entity_id=2),
    )

    response = await client.get(
        "/v1/notifications?limit=20&offset=0",
        headers={"X-User-Id": "10"},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 2
    assert data["limit"] == 20
    assert data["offset"] == 0
    assert len(data["items"]) == 2

    returned_ids = {item["entity_id"] for item in data["items"]}
    assert returned_ids == {1, 2}


@pytest.mark.asyncio
async def test_unread_count_changes_after_mark_as_read(client):
    create_response = await client.post(
        "/internal/notifications/push",
        json=make_push_payload(),
    )
    notification_id = create_response.json()["notification_id"]

    unread_before = await client.get(
        "/v1/notifications/unread-count",
        headers={"X-User-Id": "10"},
    )
    assert unread_before.status_code == 200
    assert unread_before.json()["unread_count"] == 1

    mark_response = await client.post(
        f"/v1/notifications/{notification_id}/read",
        headers={"X-User-Id": "10"},
    )
    assert mark_response.status_code == 200
    assert mark_response.json()["is_read"] is True

    unread_after = await client.get(
        "/v1/notifications/unread-count",
        headers={"X-User-Id": "10"},
    )
    assert unread_after.status_code == 200
    assert unread_after.json()["unread_count"] == 0


@pytest.mark.asyncio
async def test_mark_all_as_read_updates_all_unread_notifications(client):
    await client.post(
        "/internal/notifications/push",
        json=make_push_payload(entity_id=1),
    )
    await client.post(
        "/internal/notifications/push",
        json=make_push_payload(entity_id=2),
    )
    await client.post(
        "/internal/notifications/push",
        json=make_push_payload(entity_id=3),
    )

    unread_before = await client.get(
        "/v1/notifications/unread-count",
        headers={"X-User-Id": "10"},
    )
    assert unread_before.json()["unread_count"] == 3

    response = await client.post(
        "/v1/notifications/read-all",
        headers={"X-User-Id": "10"},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "ok"
    assert data["updated"] == 3

    unread_after = await client.get(
        "/v1/notifications/unread-count",
        headers={"X-User-Id": "10"},
    )
    assert unread_after.status_code == 200
    assert unread_after.json()["unread_count"] == 0


@pytest.mark.asyncio
async def test_mark_as_read_returns_404_for_missing_notification(client):
    response = await client.post(
        "/v1/notifications/999/read",
        headers={"X-User-Id": "10"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Notification not found"