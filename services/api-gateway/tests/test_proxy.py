import httpx


def test_projects_proxy_success(client, monkeypatch):
    class MockAsyncClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def get(self, url, headers=None, **kwargs):
            return httpx.Response(
                status_code=200,
                json={"id": 10},
                request=httpx.Request("GET", "http://identity-service/auth/me/"),
            )

        async def request(self, method, url, params=None, content=None, headers=None):
            assert method == "GET"
            assert "/v1/projects/abc" in str(url)
            assert headers["X-User-Id"] == "10"
            assert "X-Request-Id" in headers

            return httpx.Response(
                status_code=200,
                json={"project": "ok"},
                headers={"content-type": "application/json"},
                request=httpx.Request("GET", str(url)),
            )

    monkeypatch.setattr(
    "app.clients.identity.get_http_client",
    lambda: MockAsyncClient(),
    )

    monkeypatch.setattr(
        "app.services.proxy.get_http_client",
        lambda: MockAsyncClient(),
    )

    response = client.get(
        "/projects/abc",
        headers={"Authorization": "Bearer valid-token"},
    )

    assert response.status_code == 200
    assert response.json() == {"project": "ok"}
    assert "X-Request-Id" in response.headers


def test_projects_proxy_upstream_unavailable(client, monkeypatch):
    class MockAsyncClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def get(self, url, headers=None, **kwargs):
            return httpx.Response(
                status_code=200,
                json={"id": 10},
                request=httpx.Request("GET", "http://identity-service/auth/me/"),
            )

        async def request(self, method, url, params=None, content=None, headers=None):
            raise httpx.RequestError(
                "project-service down",
                request=httpx.Request(method, str(url)),
            )

    monkeypatch.setattr(
    "app.clients.identity.get_http_client",
    lambda: MockAsyncClient(),
)

    monkeypatch.setattr(
        "app.services.proxy.get_http_client",
        lambda: MockAsyncClient(),
    )

    response = client.get(
        "/projects/abc",
        headers={"Authorization": "Bearer valid-token"},
    )

    assert response.status_code == 503
    assert response.json()["detail"] == "project-service unavailable"
    assert "X-Request-Id" in response.headers