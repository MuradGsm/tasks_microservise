import pytest


@pytest.mark.asyncio
async def test_update_issue_title_creates_history(client):
    create_response = await client.post(
        "/v1/projects/1/issues",
        headers={"X-User-Id": "10"},
        json={
            "title": "Old title",
            "description": "Old description",
            "type": "TASK",
        },
    )
    issue_id = create_response.json()["id"]

    update_response = await client.patch(
        f"/v1/issues/{issue_id}",
        headers={"X-User-Id": "10"},
        json={"title": "New title"},
    )

    assert update_response.status_code == 200

    data = update_response.json()
    assert data["id"] == issue_id
    assert data["title"] == "New title"
    assert data["project_id"] == 1
    assert data["number"] == 1
    assert data["key"] == "SJ-1"
    assert data["status"] == "OPEN"
    assert data["type"] == "TASK"
    assert data["reporter_id"] == 10

    history_response = await client.get(
        f"/v1/issues/{issue_id}/history",
        headers={"X-User-Id": "10"},
    )

    assert history_response.status_code == 200

    history_data = history_response.json()
    assert len(history_data) == 1

    record = history_data[0]
    assert record["issue_id"] == issue_id
    assert record["actor_id"] == 10
    assert record["field"] == "title"
    assert record["old_value"] == "Old title"
    assert record["new_value"] == "New title"


@pytest.mark.asyncio
async def test_update_issue_multiple_fields_creates_multiple_history_records(client):
    create_response = await client.post(
        "/v1/projects/1/issues",
        headers={"X-User-Id": "10"},
        json={
            "title": "Old title",
            "description": "Old description",
            "type": "TASK",
        },
    )
    issue_id = create_response.json()["id"]

    update_response = await client.patch(
        f"/v1/issues/{issue_id}",
        headers={"X-User-Id": "10"},
        json={
            "title": "New title",
            "description": "New description",
            "type": "BUG",
        },
    )

    assert update_response.status_code == 200

    data = update_response.json()
    assert data["title"] == "New title"
    assert data["type"] == "BUG"

    history_response = await client.get(
        f"/v1/issues/{issue_id}/history",
        headers={"X-User-Id": "10"},
    )

    assert history_response.status_code == 200

    history_data = history_response.json()
    assert len(history_data) == 3

    fields = {item["field"] for item in history_data}
    assert fields == {"title", "description", "type"}

@pytest.mark.asyncio
async def test_update_issue_with_same_value_does_not_create_history(client):
    create_response = await client.post(
        "/v1/projects/1/issues",
        headers={"X-User-Id": "10"},
        json={
            "title": "Same title",
            "description": "Same description",
            "type": "TASK",
        },
    )
    issue_id = create_response.json()["id"]

    update_response = await client.patch(
        f"/v1/issues/{issue_id}",
        headers={"X-User-Id": "10"},
        json={"title": "Same title"},
    )

    assert update_response.status_code == 200

    data = update_response.json()
    assert data["title"] == "Same title"

    history_response = await client.get(
        f"/v1/issues/{issue_id}/history",
        headers={"X-User-Id": "10"},
    )

    assert history_response.status_code == 200
    assert history_response.json() == []