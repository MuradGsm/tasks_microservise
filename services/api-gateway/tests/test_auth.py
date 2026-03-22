import httpx


def test_public_ping_no_token(client):
    response = client.get("/public/ping")

    assert response.status_code == 200
    assert response.json() == {"pong": "public"}
    assert "X-Request-Id" in response.headers


def test_private_ping_missing_bearer(client):
    response = client.get("/private/ping")

    assert response.status_code == 401
    assert response.json()["detail"] == "Missing Bearer token"
    assert "X-Request-Id" in response.headers


def test_private_ping_invalid_token(client, monkeypatch):
    class MockAsyncClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def get(self, *args, **kwargs):
            return httpx.Response(
                status_code=401,
                text="Invalid token",
                request=httpx.Request("GET", "http://identity-service/auth/me/"),
            )

    monkeypatch.setattr(
    "app.clients.identity.get_http_client",
    lambda: MockAsyncClient(),
    )

    response = client.get(
        "/private/ping",
        headers={"Authorization": "Bearer bad-token"},
    )

    assert response.status_code == 401
    body = response.json()
    assert body["detail"] == "Invalid token"
    assert body["identity_status"] == 401
    assert "X-Request-Id" in response.headers


def test_private_ping_identity_unavailable(client, monkeypatch):
    class MockAsyncClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def get(self, *args, **kwargs):
            raise httpx.RequestError(
                "identity down",
                request=httpx.Request("GET", "http://identity-service/auth/me/"),
            )

    monkeypatch.setattr(
    "app.clients.identity.get_http_client",
    lambda: MockAsyncClient(),
    )

    response = client.get(
        "/private/ping",
        headers={"Authorization": "Bearer any-token"},
    )

    assert response.status_code == 503
    assert response.json()["detail"] == "Identity service unavailable"
    assert "X-Request-Id" in response.headers


def test_private_ping_valid_token(client, monkeypatch):
    class MockAsyncClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def get(self, *args, **kwargs):
            return httpx.Response(
                status_code=200,
                json={"id": 123},
                request=httpx.Request("GET", "http://identity-service/auth/me/"),
            )

    monkeypatch.setattr(
        "app.clients.identity.get_http_client",
        lambda: MockAsyncClient(),
    )

    response = client.get(
        "/private/ping",
        headers={"Authorization": "Bearer valid-token"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "pong": "private",
        "user_id": "123",
    }
    assert "X-Request-Id" in response.headers


def test_private_whoami_returns_user_id(client, monkeypatch):
    class MockAsyncClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def get(self, *args, **kwargs):
            return httpx.Response(
                status_code=200,
                json={"user_id": 77},
                request=httpx.Request("GET", "http://identity-service/auth/me/"),
            )

    monkeypatch.setattr(
        "app.clients.identity.get_http_client",
        lambda: MockAsyncClient(),
    )

    response = client.get(
        "/private/whoami",
        headers={"Authorization": "Bearer valid-token"},
    )

    assert response.status_code == 200
    assert response.json() == {"user_id": "77"}
    assert "X-Request-Id" in response.headers


def test_request_id_is_propagated_from_request_header(client):
    response = client.get(
        "/public/ping",
        headers={"X-Request-Id": "test-request-id-123"},
    )

    assert response.status_code == 200
    assert response.headers["X-Request-Id"] == "test-request-id-123"