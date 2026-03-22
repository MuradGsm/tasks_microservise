from django.db import connections
from django.db.utils import OperationalError
from django.http import JsonResponse

from identity.logging import get_logger

logger = get_logger("identity.health")
SERVICE_NAME = "identity-service"


def health(_request):
    return JsonResponse({"status": "ok", "service": SERVICE_NAME})


def ready(_request):
    try:
        connections["default"].cursor()
    except OperationalError:
        logger.warning("Readiness failed: database unavailable")
        return JsonResponse(
            {"status": "not_ready", "service": SERVICE_NAME, "db": "down"},
            status=503,
        )

    return JsonResponse(
        {"status": "ready", "service": SERVICE_NAME, "db": "ok"},
        status=200,
    )