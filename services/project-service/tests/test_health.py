import pytest

@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "project-service",
    }

@pytest.mark.asyncio
async def test_health_db(client):
    response = await client.get("/health/db")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "project-service DB",
    }