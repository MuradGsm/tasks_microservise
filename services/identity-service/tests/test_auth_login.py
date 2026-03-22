def test_login_success(api_client, user):
    response = api_client.post(
        "/auth/token/",
        {
            "username": "testuser",
            "password": "testpass123",
        },
        format="json",
    )

    assert response.status_code == 200
    data = response.json()
    assert "access" in data
    assert "refresh" in data


def test_login_fail_wrong_password(api_client, user):
    response = api_client.post(
        "/auth/token/",
        {
            "username": "testuser",
            "password": "wrongpass",
        },
        format="json",
    )

    assert response.status_code == 401