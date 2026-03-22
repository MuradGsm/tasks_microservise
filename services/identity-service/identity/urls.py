from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include

from accounts.jwt_views import LoggedTokenObtainPairView, LoggedTokenRefreshView
from accounts.views import me
from identity.logging import get_logger
from identity.health import ready, health

logger = get_logger("identity.urls")



urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health),

    path("auth/token/", LoggedTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", LoggedTokenRefreshView.as_view(), name="token_refresh"),

    path("auth/me/", me, name="me"),

    path("", include("django_prometheus.urls")),
    path("health/", health),
    path("ready/", ready),
]