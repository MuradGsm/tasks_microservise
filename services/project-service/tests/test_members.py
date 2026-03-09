import pytest

@pytest.mark.asyncio
async def test_add_member(client):
    create_project_response = await client.post(
        "/v1/projects",
        headers={"X-User-Id":"1"},
        json={"key": "SJ", "name": "Sjira"}
    )
    project_id = create_project_response.json()["id"]

    response = await client.post(
        f"/v1/projects/{project_id}/members",
        headers={"X-User-Id":"1"},
        json={"user_id":2, "role": "MEMBER"}
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == 1
    assert data["project_id"] == project_id
    assert data["user_id"] == 2
    assert data["role"] == "MEMBER"

@pytest.mark.asyncio
async def test_owner_cannot_be_added_as_member(client):
    create_project_response = await client.post(
        "/v1/projects",
        headers={"X-User-Id":"1"},
        json={"key": "SJ", "name": "Sjira"}
    )
    project_id = create_project_response.json()["id"]

    response = await client.post(
        f"/v1/projects/{project_id}/members",
        headers={"X-User-Id":"1"},
        json={"user_id":1, "role": "MEMBER"}
    )

    assert response.status_code == 400

    data = response.json()["detail"] == "Owner is already part of the project"

@pytest.mark.asyncio
async def test_add_duplicate_members_returns_409(client):
    create_project_response = await client.post(
        "/v1/projects",
        headers={"X-User-Id":"1"},
        json={"key": "SJ", "name": "Sjira"}
    )
    project_id = create_project_response.json()["id"]

    first_response = await client.post(
        f"/v1/projects/{project_id}/members",
        headers={"X-User-Id":"1"},
        json={"user_id":2, "role": "MEMBER"}
    )
    assert first_response.status_code == 200

    response = await client.post(
        f"/v1/projects/{project_id}/members",
        headers={"X-User-Id":"1"},
        json={"user_id":2, "role": "MEMBER"}
    )
    assert response.status_code == 409

    data = response.json()["detail"] == "User is alerady a member of this project"

@pytest.mark.asyncio
async def test_foreign_user_cannot_add_member(client):
    create_project_response = await client.post(
        "/v1/projects",
        headers={"X-User-Id":"1"},
        json={"key": "SJ", "name": "Sjira"}
    )
    project_id = create_project_response.json()["id"]


    response = await client.post(
        f"/v1/projects/{project_id}/members",
        headers={"X-User-Id":"2"},
        json={"user_id":3, "role": "MEMBER"}
    )

    assert response.status_code == 404

    data = response.json()["detail"] == "Project not found"


@pytest.mark.asyncio
async def test_lis_members(client):
    create_project_response = await client.post(
        "/v1/projects",
        headers={"X-User-Id":"1"},
        json={"key": "SJ", "name": "Sjira"}
    )
    project_id = create_project_response.json()["id"]


    await client.post(
        f"/v1/projects/{project_id}/members",
        headers={"X-User-Id": "1"},
        json={"user_id": 2, "role": "MEMBER"},
    )

    await client.post(
        f"/v1/projects/{project_id}/members",
        headers={"X-User-Id": "1"},
        json={"user_id": 3, "role": "MEMBER"},
    )

    response = await client.get(
        f'/v1/projects/{project_id}/members',
        headers={"X-User-Id":"1"},
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

    user_ids = {item['user_id'] for item in data}
    assert user_ids == {2,3}

@pytest.mark.asyncio
async def test_foreign_user_cannot_list_member(client):
    create_project_response = await client.post(
        "/v1/projects",
        headers={"X-User-Id":"1"},
        json={"key": "SJ", "name": "Sjira"}
    )
    project_id = create_project_response.json()["id"]


    response = await client.get(
        f"/v1/projects/{project_id}/members",
        headers={"X-User-Id":"2"},
    )
    assert response.status_code == 404

    data = response.json()["detail"] == "Project not found"

@pytest.mark.asyncio
async def test_delete_member(client):
    create_project_response = await client.post(
        "/v1/projects",
        headers={"X-User-Id": "1"},
        json={"key": "SJ", "name": "SJira"},
    )
    project_id = create_project_response.json()["id"]

    add_response = await client.post(
        f"/v1/projects/{project_id}/members",
        headers={"X-User-Id": "1"},
        json={"user_id": 2, "role": "MEMBER"},
    )
    member_id = add_response.json()["id"]

    delete_response = await client.delete(
        f"/v1/projects/{project_id}/members/{member_id}",
        headers={"X-User-Id": "1"},
    )

    assert delete_response.status_code == 204
    assert delete_response.text == ""

    list_response = await client.get(
        f"/v1/projects/{project_id}/members",
        headers={"X-User-Id": "1"},
    )

    assert list_response.status_code == 200
    assert list_response.json() == []

@pytest.mark.asyncio
async def test_delete_missing_member_returns_404(client):
    create_project_response = await client.post(
        "/v1/projects",
        headers={"X-User-Id": "1"},
        json={"key": "SJ", "name": "SJira"},
    )
    project_id = create_project_response.json()["id"]

    response = await client.delete(
        f"/v1/projects/{project_id}/members/999",
        headers={"X-User-Id": "1"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Project memeber not found!"

@pytest.mark.asyncio
async def test_foreign_user_cannot_delete_member(client):
    create_project_response = await client.post(
        "/v1/projects",
        headers={"X-User-Id": "1"},
        json={"key": "SJ", "name": "SJira"},
    )
    project_id = create_project_response.json()["id"]

    add_response = await client.post(
        f"/v1/projects/{project_id}/members",
        headers={"X-User-Id": "1"},
        json={"user_id": 2, "role": "MEMBER"},
    )
    member_id = add_response.json()["id"]

    response = await client.delete(
        f"/v1/projects/{project_id}/members/{member_id}",
        headers={"X-User-Id": "2"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"

@pytest.mark.asyncio
async def test_access_returns_true_for_owner(client):
    create_project_response = await client.post(
        "/v1/projects",
        headers={"X-User-Id": "1"},
        json={"key": "SJ", "name": "SJira"},
    )
    project_id = create_project_response.json()["id"]

    response = await client.get(
        f"/v1/projects/{project_id}/access/1"
    )

    assert response.status_code == 200
    assert response.json() == {"has_access": True}

@pytest.mark.asyncio
async def test_access_returns_true_for_member(client):
    create_project_response = await client.post(
        "/v1/projects",
        headers={"X-User-Id": "1"},
        json={"key": "SJ", "name": "SJira"},
    )
    project_id = create_project_response.json()["id"]

    await client.post(
        f"/v1/projects/{project_id}/members",
        headers={"X-User-Id": "1"},
        json={"user_id": 2, "role": "MEMBER"},
    )

    response = await client.get(
        f"/v1/projects/{project_id}/access/2"
    )

    assert response.status_code == 200
    assert response.json() == {"has_access": True}

@pytest.mark.asyncio
async def test_access_returns_false_for_foreign_user(client):
    create_project_response = await client.post(
        "/v1/projects",
        headers={"X-User-Id": "1"},
        json={"key": "SJ", "name": "SJira"},
    )
    project_id = create_project_response.json()["id"]

    response = await client.get(
        f"/v1/projects/{project_id}/access/999"
    )

    assert response.status_code == 200
    assert response.json() == {"has_access": False}

@pytest.mark.asyncio
async def test_access_returns_false_for_missing_project(client):
    response = await client.get("/v1/projects/999/access/1")

    assert response.status_code == 200
    assert response.json() == {"has_access": False}