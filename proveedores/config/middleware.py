import hmac
import os
import uuid
import logging
from django.http import JsonResponse

logger = logging.getLogger(__name__)

class InternalTokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.token = os.environ.get("INTERNAL_TOKEN", "")
    def __call__(self, request):
        correlation_id = request.headers.get("X-Correlation-Id") or str(uuid.uuid4())
        request.correlation_id = correlation_id
        logger.info("%s %s correlation_id=%s", request.method, request.path, correlation_id)
        if request.path != "/health":
            received = request.headers.get("X-Internal-Token", "")
            if not self.token or not hmac.compare_digest(received.encode(), self.token.encode()):
                return JsonResponse({
                    "error": "TOKEN_INTERNO_INVALIDO",
                    "message": "Esta ruta solo la puede usar el API Gateway",
                    "correlation_id": correlation_id,
                }, status=401)
        response = self.get_response(request)
        response["X-Correlation-Id"] = correlation_id
        return response