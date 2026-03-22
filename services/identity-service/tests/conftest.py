import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    User = get_user_model()
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
    )


@pytest.fixture
def auth_tokens(api_client, user):
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
    return {
        "access": data["access"],
        "refresh": data["refresh"],
    }