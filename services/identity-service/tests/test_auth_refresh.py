def test_refresh_success(api_client, auth_tokens):
    response = api_client.post(
        "/auth/token/refresh/",
        {
            "refresh": auth_tokens["refresh"],
        },
        format="json",
    )

    assert response.status_code == 200
    data = response.json()
    assert "access" in data


def test_refresh_fail_invalid_token(api_client):
    response = api_client.post(
        "/auth/token/refresh/",
        {
            "refresh": "invalid-token",
        },
        format="json",
    )

    assert response.status_code == 401