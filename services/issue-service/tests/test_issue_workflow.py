import pytest


@pytest.mark.asyncio
async def test_transition_open_to_in_progress(client):
    create_response = await client.post(
        "/v1/projects/1/issues",
        headers={"X-User-Id": "10"},
        json={
            "title": "Workflow issue",
            "description": "Desc",
            "type": "TASK",
        },
    )
    issue_id = create_response.json()["id"]

    transition_response = await client.post(
        f"/v1/issues/{issue_id}/transitions",
        headers={"X-User-Id": "10"},
        json={"to_status": "IN_PROGRESS"},
    )

    assert transition_response.status_code == 200

    data = transition_response.json()
    assert data["issue_id"] == issue_id
    assert data["from_status"] == "OPEN"
    assert data["to_status"] == "IN_PROGRESS"

    get_response = await client.get(
        f"/v1/issues/{issue_id}",
        headers={"X-User-Id": "10"},
    )

    assert get_response.status_code == 200
    issue_data = get_response.json()
    assert issue_data["status"] == "IN_PROGRESS"


@pytest.mark.asyncio
async def test_transition_open_to_done_returns_409(client):
    create_response = await client.post(
        "/v1/projects/1/issues",
        headers={"X-User-Id": "10"},
        json={
            "title": "Workflow issue",
            "description": "Desc",
            "type": "TASK",
        },
    )
    issue_id = create_response.json()["id"]

    transition_response = await client.post(
        f"/v1/issues/{issue_id}/transitions",
        headers={"X-User-Id": "10"},
        json={"to_status": "DONE"},
    )

    assert transition_response.status_code == 409
    assert transition_response.json()["detail"] == "Transition not allowed: OPEN -> DONE"

@pytest.mark.asyncio
async def test_transition_with_invalid_status_returns_422(client):
    create_response = await client.post(
        "/v1/projects/1/issues",
        headers={"X-User-Id": "10"},
        json={
            "title": "Workflow issue",
            "description": "Desc",
            "type": "TASK",
        },
    )
    issue_id = create_response.json()["id"]

    transition_response = await client.post(
        f"/v1/issues/{issue_id}/transitions",
        headers={"X-User-Id": "10"},
        json={"to_status": "CLOSED"},
    )

    assert transition_response.status_code == 422
    assert transition_response.json()["detail"] == "Invalid status"

@pytest.mark.asyncio
async def test_transition_creates_history_record(client):
    create_response = await client.post(
        "/v1/projects/1/issues",
        headers={"X-User-Id": "10"},
        json={
            "title": "Workflow issue",
            "description": "Desc",
            "type": "TASK",
        },
    )
    issue_id = create_response.json()["id"]

    transition_response = await client.post(
        f"/v1/issues/{issue_id}/transitions",
        headers={"X-User-Id": "10"},
        json={"to_status": "IN_PROGRESS"},
    )

    assert transition_response.status_code == 200

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
    assert record["field"] == "status"
    assert record["old_value"] == "OPEN"
    assert record["new_value"] == "IN_PROGRESS"