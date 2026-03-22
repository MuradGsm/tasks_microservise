def test_me_success(api_client, auth_tokens):
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {auth_tokens['access']}")

    response = api_client.get("/auth/me/")

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"


def test_me_unauthorized(api_client):
    response = api_client.get("/auth/me/")
    assert response.status_code == 401