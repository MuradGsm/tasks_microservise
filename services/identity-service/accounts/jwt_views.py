from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from identity.logging import get_logger
from identity.metrics import (
    identity_login_success_total,
    identity_login_failed_total,
    identity_token_refresh_total,
    identity_token_refresh_failed_total,
)

logger = get_logger("accounts.jwt_views")


class LoggedTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        username = request.data.get("username", "")

        logger.info(
            "Token obtain requested",
            extra={
                "path": request.path,
                "method": request.method,
                "username": username,
            },
        )

        response = super().post(request, *args, **kwargs)

        if response.status_code == status.HTTP_200_OK:
            identity_login_success_total.inc()

            logger.info(
                "Token issued",
                extra={
                    "path": request.path,
                    "method": request.method,
                    "username": username,
                },
            )
        else:
            identity_login_failed_total.inc()

            logger.warning(
                "Token obtain failed",
                extra={
                    "path": request.path,
                    "method": request.method,
                    "username": username,
                    "status_code": response.status_code,
                },
            )

        return response


class LoggedTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        logger.info(
            "Token refresh requested",
            extra={
                "path": request.path,
                "method": request.method,
            },
        )

        response = super().post(request, *args, **kwargs)

        if response.status_code == status.HTTP_200_OK:
            identity_token_refresh_total.inc()

            logger.info(
                "Token refreshed",
                extra={
                    "path": request.path,
                    "method": request.method,
                },
            )
        else:
            identity_token_refresh_failed_total.inc()

            logger.warning(
                "Token refresh failed",
                extra={
                    "path": request.path,
                    "method": request.method,
                    "status_code": response.status_code,
                },
            )

        return response 