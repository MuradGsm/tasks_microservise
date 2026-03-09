import pytest


@pytest.mark.asyncio
async def test_update_issue_assignee_when_user_has_project_access(client, project_service_mock):
    project_service_mock["assignee_has_access"] = True

    create_response = await client.post(
        "/v1/projects/1/issues",
        headers={"X-User-Id": "10"},
        json={
            "title": "Issue for assignee",
            "description": "Desc",
            "type": "TASK",
        },
    )
    issue_id = create_response.json()["id"]

    update_response = await client.patch(
        f"/v1/issues/{issue_id}",
        headers={"X-User-Id": "10"},
        json={"assignee_id": 20},
    )

    assert update_response.status_code == 200

    data = update_response.json()
    assert data["id"] == issue_id
    assert data["title"] == "Issue for assignee"
    assert data["key"] == "SJ-1"


@pytest.mark.asyncio
async def test_update_issue_assignee_without_project_access_returns_400(client, project_service_mock):
    project_service_mock["assignee_has_access"] = False

    create_response = await client.post(
        "/v1/projects/1/issues",
        headers={"X-User-Id": "10"},
        json={
            "title": "Issue for forbidden assignee",
            "description": "Desc",
            "type": "TASK",
        },
    )
    issue_id = create_response.json()["id"]

    update_response = await client.patch(
        f"/v1/issues/{issue_id}",
        headers={"X-User-Id": "10"},
        json={"assignee_id": 999},
    )

    assert update_response.status_code == 400
    assert update_response.json()["detail"] == "Assignee must be a project member or owner"


@pytest.mark.asyncio
async def test_update_issue_assignee_creates_history_record(client, project_service_mock):
    project_service_mock["assignee_has_access"] = True

    create_response = await client.post(
        "/v1/projects/1/issues",
        headers={"X-User-Id": "10"},
        json={
            "title": "Issue with assignee history",
            "description": "Desc",
            "type": "TASK",
        },
    )
    issue_id = create_response.json()["id"]

    update_response = await client.patch(
        f"/v1/issues/{issue_id}",
        headers={"X-User-Id": "10"},
        json={"assignee_id": 20},
    )

    assert update_response.status_code == 200

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
    assert record["field"] == "assignee_id"
    assert record["old_value"] is None
    assert record["new_value"] == "20"


@pytest.mark.asyncio
async def test_update_issue_with_same_assignee_does_not_create_extra_history(client, project_service_mock):
    project_service_mock["assignee_has_access"] = True

    create_response = await client.post(
        "/v1/projects/1/issues",
        headers={"X-User-Id": "10"},
        json={
            "title": "Issue same assignee",
            "description": "Desc",
            "type": "TASK",
        },
    )
    issue_id = create_response.json()["id"]

    first_update = await client.patch(
        f"/v1/issues/{issue_id}",
        headers={"X-User-Id": "10"},
        json={"assignee_id": 20},
    )
    assert first_update.status_code == 200

    second_update = await client.patch(
        f"/v1/issues/{issue_id}",
        headers={"X-User-Id": "10"},
        json={"assignee_id": 20},
    )
    assert second_update.status_code == 200

    history_response = await client.get(
        f"/v1/issues/{issue_id}/history",
        headers={"X-User-Id": "10"},
    )

    assert history_response.status_code == 200

    history_data = history_response.json()
    assert len(history_data) == 1
    assert history_data[0]["field"] == "assignee_id"
    assert history_data[0]["new_value"] == "20"