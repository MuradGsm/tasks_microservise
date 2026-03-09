import pytest


@pytest.mark.asyncio
async def test_create_comment(client):
    create_issue_response = await client.post(
        "/v1/projects/1/issues",
        headers={"X-User-Id": "10"},
        json={
            "title": "Issue with comment",
            "description": "Desc",
            "type": "TASK",
        },
    )
    issue_id = create_issue_response.json()["id"]

    response = await client.post(
        f"/v1/issues/{issue_id}/comments",
        headers={"X-User-Id": "10"},
        json={"text": "First comment"},
    )

    assert response.status_code == 201

    data = response.json()
    assert data["id"] == 1
    assert data["issue_id"] == issue_id
    assert data["author_id"] == 10
    assert data["text"] == "First comment"
    assert "created_at" in data

@pytest.mark.asyncio
async def test_list_comments(client):
    create_issue_response = await client.post(
        "/v1/projects/1/issues",
        headers={"X-User-Id": "10"},
        json={
            "title": "Issue with comments",
            "description": "Desc",
            "type": "TASK",
        },
    )
    issue_id = create_issue_response.json()["id"]

    await client.post(
        f"/v1/issues/{issue_id}/comments",
        headers={"X-User-Id": "10"},
        json={"text": "First comment"},
    )

    await client.post(
        f"/v1/issues/{issue_id}/comments",
        headers={"X-User-Id": "10"},
        json={"text": "Second comment"},
    )

    response = await client.get(
        f"/v1/issues/{issue_id}/comments",
        headers={"X-User-Id": "10"},
    )

    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2

    assert data[0]["text"] == "First comment"
    assert data[0]["author_id"] == 10

    assert data[1]["text"] == "Second comment"
    assert data[1]["author_id"] == 10

@pytest.mark.asyncio
async def test_list_comments_with_pagination(client):
    create_issue_response = await client.post(
        "/v1/projects/1/issues",
        headers={"X-User-Id": "10"},
        json={
            "title": "Issue with many comments",
            "description": "Desc",
            "type": "TASK",
        },
    )
    issue_id = create_issue_response.json()["id"]

    await client.post(
        f"/v1/issues/{issue_id}/comments",
        headers={"X-User-Id": "10"},
        json={"text": "Comment 1"},
    )
    await client.post(
        f"/v1/issues/{issue_id}/comments",
        headers={"X-User-Id": "10"},
        json={"text": "Comment 2"},
    )
    await client.post(
        f"/v1/issues/{issue_id}/comments",
        headers={"X-User-Id": "10"},
        json={"text": "Comment 3"},
    )

    response = await client.get(
        f"/v1/issues/{issue_id}/comments?limit=2&offset=1",
        headers={"X-User-Id": "10"},
    )

    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2
    assert data[0]["text"] == "Comment 2"
    assert data[1]["text"] == "Comment 3"

@pytest.mark.asyncio
async def test_cannot_create_comment_for_deleted_issue(client):
    create_issue_response = await client.post(
        "/v1/projects/1/issues",
        headers={"X-User-Id": "10"},
        json={
            "title": "Issue to delete",
            "description": "Desc",
            "type": "TASK",
        },
    )
    issue_id = create_issue_response.json()["id"]

    delete_response = await client.delete(
        f"/v1/issues/{issue_id}",
        headers={"X-User-Id": "10"},
    )
    assert delete_response.status_code == 204

    response = await client.post(
        f"/v1/issues/{issue_id}/comments",
        headers={"X-User-Id": "10"},
        json={"text": "Should fail"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Issue not found"