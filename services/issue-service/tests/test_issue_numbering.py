import pytest

@pytest.mark.asyncio
async def test_issue_numbering_in_same_project(client):
    await client.post(
        "/v1/projects/1/issues",
        headers={"X-User-Id": "10"},
        json={
            "title": "First",
            "description": "First",
            "type": "TASK",
        },
    )

    second = await client.post(
        "/v1/projects/1/issues",
        headers={"X-User-Id": "10"},
        json={
            "title": "Second",
            "description": "Second",
            "type": "TASK",
        },
    )

    data = second.json()

    assert data["number"] == 2
    assert data["key"] == "SJ-2"


@pytest.mark.asyncio
async def test_issue_numbering_separate_projects(client, project_service_mock):
    project_service_mock["project_key"] = "SJ"

    await client.post(
        "/v1/projects/1/issues",
        headers={"X-User-Id": "10"},
        json={"title": "First", "description": "First", "type": "TASK"},
    )

    project_service_mock["project_key"] = "API"

    response = await client.post(
        "/v1/projects/2/issues",
        headers={"X-User-Id": "10"},
        json={"title": "Second", "description": "Second", "type": "TASK"},
    )

    data = response.json()

    assert data["number"] == 1
    assert data["key"] == "API-1"