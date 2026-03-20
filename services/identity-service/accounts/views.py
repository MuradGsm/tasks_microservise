from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from identity.logging import get_logger

logger = get_logger("accounts.views")


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    user = request.user

    logger.info(
        "Authenticated user resolved",
        extra={
            "user_id": user.id,
            "path": request.path,
            "method": request.method,
        },
    )

    return Response(
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_staff": user.is_staff,
        }
    )