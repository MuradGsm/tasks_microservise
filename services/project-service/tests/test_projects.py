import pytest


@pytest.mark.asyncio
async def test_create_project(client):
    response = await client.post(
        "/v1/projects",
        headers={"X-User-Id": "1"},
        json={"key": "SJ", "name": "SJira"},
    )

    assert response.status_code == 201

    data = response.json()
    assert data["id"] == 1
    assert data["key"] == "SJ"
    assert data["name"] == "SJira"
    assert data["owner_id"] == 1


@pytest.mark.asyncio
async def test_list_projects_returns_only_owner_projects(client):
    await client.post(
        "/v1/projects",
        headers={"X-User-Id": "1"},
        json={"key": "SJ", "name": "SJira"},
    )

    await client.post(
        "/v1/projects",
        headers={"X-User-Id": "2"},
        json={"key": "AB", "name": "Another"},
    )

    response = await client.get(
        "/v1/projects",
        headers={"X-User-Id": "1"},
    )

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1
    assert data[0]["key"] == "SJ"
    assert data[0]["owner_id"] == 1


@pytest.mark.asyncio
async def test_get_project_by_id_for_owner(client):
    create_response = await client.post(
        "/v1/projects",
        headers={"X-User-Id": "1"},
        json={"key": "SJ", "name": "SJira"},
    )
    project_id = create_response.json()["id"]

    response = await client.get(
        f"/v1/projects/{project_id}",
        headers={"X-User-Id": "1"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == project_id
    assert data["key"] == "SJ"
    assert data["owner_id"] == 1


@pytest.mark.asyncio
async def test_get_project_by_id_for_foreign_user_returns_404(client):
    create_response = await client.post(
        "/v1/projects",
        headers={"X-User-Id": "1"},
        json={"key": "SJ", "name": "SJira"},
    )
    project_id = create_response.json()["id"]

    response = await client.get(
        f"/v1/projects/{project_id}",
        headers={"X-User-Id": "2"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"

@pytest.mark.asyncio
async def test_create_project_with_duplicate_key_returns_409(client):
    await client.post(
        '/v1/projects',
        headers={"X-User-Id":"1"},
        json={"key": "SJ", "name": "SJira"}
    )

    response = await client.post(
        "/v1/projects",
        headers={"X-User-Id": "2"},
        json={"key": "SJ", "name": "Another Project"},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Project key already exists"

@pytest.mark.asyncio
async def test_update_project_name(client):
    create_response = await client.post(
        "/v1/projects",
        headers={"X-User-Id": "1"},
        json={"key": "SJ", "name": "SJira"},
    )
    project_id = create_response.json()["id"]

    response = await client.patch(
        f"/v1/projects/{project_id}",
        headers={"X-User-Id": "1"},
        json={"name": "SJira Updated"},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == project_id
    assert data["key"] == "SJ"
    assert data["name"] == "SJira Updated"
    assert data["owner_id"] == 1

@pytest.mark.asyncio
async def test_update_project_name(client):
    create_response = await client.post(
        "/v1/projects",
        headers={"X-User-Id": "1"},
        json={"key": "SJ", "name": "SJira"},
    )
    project_id = create_response.json()["id"]

    response = await client.patch(
        f"/v1/projects/{project_id}",
        headers={"X-User-Id": "1"},
        json={"name": "SJira Updated"},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == project_id
    assert data["key"] == "SJ"
    assert data["name"] == "SJira Updated"
    assert data["owner_id"] == 1


@pytest.mark.asyncio
async def test_foreign_user_cannot_update_project(client):
    create_response = await client.post(
        "/v1/projects",
        headers={"X-User-Id": "1"},
        json={"key": "SJ", "name": "SJira"},
    )
    project_id = create_response.json()["id"]

    response = await client.patch(
        f"/v1/projects/{project_id}",
        headers={"X-User-Id": "2"},
        json={"name": "Hacked Name"},
    )

    assert response.status_code == 404

    assert response.json()["detail"] == "Project not found"

@pytest.mark.asyncio
async def test_delete_project(client):
    create_response = await client.post(
        "/v1/projects",
        headers={"X-User-Id": "1"},
        json={"key": "SJ", "name": "SJira"},
    )
    project_id = create_response.json()["id"]

    delete_response = await client.delete(
        f"/v1/projects/{project_id}",
        headers={"X-User-Id": "1"},
    )

    assert delete_response.status_code == 204
    assert delete_response.text == ""

    get_response = await client.get(
        f"/v1/projects/{project_id}",
        headers={"X-User-Id": "1"},
    )

    assert get_response.status_code == 404
    assert get_response.json()["detail"] == "Project not found"

@pytest.mark.asyncio
async def test_foreign_user_cannot_delete_project(client):
    create_response = await client.post(
        "/v1/projects",
        headers={"X-User-Id": "1"},
        json={"key": "SJ", "name": "SJira"},
    )
    project_id = create_response.json()["id"]

    response = await client.delete(
        f"/v1/projects/{project_id}",
        headers={"X-User-Id": "2"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"