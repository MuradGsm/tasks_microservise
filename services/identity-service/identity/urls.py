from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from accounts.views import me

def health(_request):
    return JsonResponse({"status": "ok", "service": "identity-service"})

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health),

    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name='token_refresh'),

    path('auth/me/', me, name='me')
]