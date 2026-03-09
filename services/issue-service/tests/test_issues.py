import pytest


@pytest.mark.asyncio
async def test_create_issue(client):
    response = await client.post(
        "/v1/projects/1/issues",
        headers={"X-User-Id": "10"},
        json={
            "title": "First issue",
            "description": "First description",
            "type": "TASK",
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["id"] == 1
    assert data["project_id"] == 1
    assert data["number"] == 1
    assert data["key"] == "SJ-1"
    assert data["title"] == "First issue"
    assert data["status"] == "OPEN"
    assert data["type"] == "TASK"
    assert data["reporter_id"] == 10

@pytest.mark.asyncio
async def test_list_issues_by_project(client):
    await client.post(
        "/v1/projects/1/issues",
        headers={"X-User-Id": "10"},
        json={
            "title": "First issue",
            "description": "First description",
            "type": "TASK",
        },
    )

    await client.post(
        "/v1/projects/1/issues",
        headers={"X-User-Id": "10"},
        json={
            "title": "Second issue",
            "description": "Second description",
            "type": "BUG",
        },
    )

    response = await client.get(
        "/v1/projects/1/issues",
        headers={"X-User-Id": "10"},
    )

    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2

    assert data[0]["number"] == 1
    assert data[0]["key"] == "SJ-1"
    assert data[0]["title"] == "First issue"

    assert data[1]["number"] == 2
    assert data[1]["key"] == "SJ-2"
    assert data[1]["title"] == "Second issue"

@pytest.mark.asyncio
async def test_get_issue_by_id(client):
    create_response = await client.post(
        "/v1/projects/1/issues",
        headers={"X-User-Id": "10"},
        json={
            "title": "First issue",
            "description": "First description",
            "type": "TASK",
        },
    )
    issue_id = create_response.json()["id"]

    response = await client.get(
        f"/v1/issues/{issue_id}",
        headers={"X-User-Id": "10"},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == issue_id
    assert data["project_id"] == 1
    assert data["number"] == 1
    assert data["key"] == "SJ-1"
    assert data["title"] == "First issue"
    assert data["status"] == "OPEN"
    assert data["type"] == "TASK"
    assert data["reporter_id"] == 10

@pytest.mark.asyncio
async def test_delete_issue_soft_delete(client):
    create_response = await client.post(
        "/v1/projects/1/issues",
        headers={"X-User-Id": "10"},
        json={
            "title": "First issue",
            "description": "First description",
            "type": "TASK",
        },
    )
    issue_id = create_response.json()["id"]

    delete_response = await client.delete(
        f"/v1/issues/{issue_id}",
        headers={"X-User-Id": "10"},
    )

    assert delete_response.status_code == 204
    assert delete_response.text == ""

    get_response = await client.get(
        f"/v1/issues/{issue_id}",
        headers={"X-User-Id": "10"},
    )

    assert get_response.status_code == 404
    assert get_response.json()["detail"] == "Issue not found"

@pytest.mark.asyncio
async def test_deleted_issue_not_in_list(client):
    first_response = await client.post(
        "/v1/projects/1/issues",
        headers={"X-User-Id": "10"},
        json={
            "title": "First issue",
            "description": "First description",
            "type": "TASK",
        },
    )
    first_issue_id = first_response.json()["id"]

    await client.post(
        "/v1/projects/1/issues",
        headers={"X-User-Id": "10"},
        json={
            "title": "Second issue",
            "description": "Second description",
            "type": "BUG",
        },
    )

    await client.delete(
        f"/v1/issues/{first_issue_id}",
        headers={"X-User-Id": "10"},
    )

    response = await client.get(
        "/v1/projects/1/issues",
        headers={"X-User-Id": "10"},
    )

    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Second issue"
    assert data[0]["key"] == "SJ-2"

