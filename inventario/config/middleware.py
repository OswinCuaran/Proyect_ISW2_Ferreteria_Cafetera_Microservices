"""Middleware del microservicio: token interno, correlation id y log de cada petición."""
import hmac
import logging
import time
import uuid
from django.conf import settings
from django.http import JsonResponse

logger = logging.getLogger("inventario")

class InternalTokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        correlation_id = request.headers.get("X-Correlation-Id") or str(uuid.uuid4())
        request.correlation_id = correlation_id
        start = time.monotonic()
        if request.path != "/health" and not self._valid_token(request):
            response = JsonResponse({
                "error": "TOKEN_INTERNO_INVALIDO",
                "message": "Esta ruta solo la puede usar el API Gateway",
                "correlation_id": correlation_id,
            }, status=401, json_dumps_params={"ensure_ascii": False})
        else:
            response = self.get_response(request)
        response["X-Correlation-Id"] = correlation_id
        logger.info(
            "%s %s %s %sms user_id=%s correlation_id=%s",
            request.method, request.path, response.status_code,
            round((time.monotonic() - start) * 1000),
            request.headers.get("X-User-Id", "-"), correlation_id,
        )
        return response

    @staticmethod
    def _valid_token(request):
        expected = settings.INTERNAL_TOKEN
        received = request.headers.get("X-Internal-Token", "")
        return bool(expected) and hmac.compare_digest(received.encode(), expected.encode())
