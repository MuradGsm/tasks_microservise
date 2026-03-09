import pytest


@pytest.mark.asyncio
async def test_filter_issues_by_status(client):
    first_response = await client.post(
        "/v1/projects/1/issues",
        headers={"X-User-Id": "10"},
        json={
            "title": "Open issue",
            "description": "Desc",
            "type": "TASK",
        },
    )
    first_issue_id = first_response.json()["id"]

    await client.post(
        f"/v1/issues/{first_issue_id}/transitions",
        headers={"X-User-Id": "10"},
        json={"to_status": "IN_PROGRESS"},
    )

    await client.post(
        "/v1/projects/1/issues",
        headers={"X-User-Id": "10"},
        json={
            "title": "Still open issue",
            "description": "Desc",
            "type": "TASK",
        },
    )

    response = await client.get(
        "/v1/projects/1/issues?status=IN_PROGRESS",
        headers={"X-User-Id": "10"},
    )

    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Open issue"
    assert data[0]["status"] == "IN_PROGRESS"

@pytest.mark.asyncio
async def test_filter_issues_by_type(client):
    await client.post(
        "/v1/projects/1/issues",
        headers={"X-User-Id": "10"},
        json={
            "title": "Bug issue",
            "description": "Bug desc",
            "type": "BUG",
        },
    )

    await client.post(
        "/v1/projects/1/issues",
        headers={"X-User-Id": "10"},
        json={
            "title": "Task issue",
            "description": "Task desc",
            "type": "TASK",
        },
    )

    response = await client.get(
        "/v1/projects/1/issues?type=BUG",
        headers={"X-User-Id": "10"},
    )

    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Bug issue"
    assert data[0]["type"] == "BUG"

@pytest.mark.asyncio
async def test_filter_issues_by_reporter_id(client):
    await client.post(
        "/v1/projects/1/issues",
        headers={"X-User-Id": "10"},
        json={
            "title": "Reporter 10 issue",
            "description": "Desc",
            "type": "TASK",
        },
    )

    await client.post(
        "/v1/projects/1/issues",
        headers={"X-User-Id": "20"},
        json={
            "title": "Reporter 20 issue",
            "description": "Desc",
            "type": "TASK",
        },
    )

    response = await client.get(
        "/v1/projects/1/issues?reporter_id=20",
        headers={"X-User-Id": "10"},
    )

    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Reporter 20 issue"
    assert data[0]["reporter_id"] == 20

@pytest.mark.asyncio
async def test_search_issues_by_q(client):
    await client.post(
        "/v1/projects/1/issues",
        headers={"X-User-Id": "10"},
        json={
            "title": "Login bug",
            "description": "User cannot login",
            "type": "BUG",
        },
    )

    await client.post(
        "/v1/projects/1/issues",
        headers={"X-User-Id": "10"},
        json={
            "title": "Registration task",
            "description": "Create registration form",
            "type": "TASK",
        },
    )

    response = await client.get(
        "/v1/projects/1/issues?q=login",
        headers={"X-User-Id": "10"},
    )

    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Login bug"

@pytest.mark.asyncio
async def test_search_issues_by_q(client):
    await client.post(
        "/v1/projects/1/issues",
        headers={"X-User-Id": "10"},
        json={
            "title": "Login bug",
            "description": "User cannot login",
            "type": "BUG",
        },
    )

    await client.post(
        "/v1/projects/1/issues",
        headers={"X-User-Id": "10"},
        json={
            "title": "Registration task",
            "description": "Create registration form",
            "type": "TASK",
        },
    )

    response = await client.get(
        "/v1/projects/1/issues?q=login",
        headers={"X-User-Id": "10"},
    )

    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Login bug"

@pytest.mark.asyncio
async def test_list_issues_with_limit_and_offset(client):
    await client.post(
        "/v1/projects/1/issues",
        headers={"X-User-Id": "10"},
        json={"title": "Issue 1", "description": "Desc", "type": "TASK"},
    )
    await client.post(
        "/v1/projects/1/issues",
        headers={"X-User-Id": "10"},
        json={"title": "Issue 2", "description": "Desc", "type": "TASK"},
    )
    await client.post(
        "/v1/projects/1/issues",
        headers={"X-User-Id": "10"},
        json={"title": "Issue 3", "description": "Desc", "type": "TASK"},
    )

    response = await client.get(
        "/v1/projects/1/issues?limit=2&offset=1",
        headers={"X-User-Id": "10"},
    )

    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Issue 2"
    assert data[1]["title"] == "Issue 3"

@pytest.mark.asyncio
async def test_filter_issues_with_invalid_status_returns_422(client):
    response = await client.get(
        "/v1/projects/1/issues?status=CLOSED",
        headers={"X-User-Id": "10"},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "Invalid status"