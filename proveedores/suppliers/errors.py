import logging

from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)

def error_response(request, status, code, message, errors=None):
    body = {
        "error": code,
        "message": message,
        "correlation_id": getattr(request, "correlation_id", ""),
    }
    if errors:
        body["errors"] = errors
    return Response(body, status=status)

def custom_exception_handler(exc, context):
    request = context["request"]
    response = exception_handler(exc, context)
    if response is None:
        logger.exception(
            "Error inesperado correlation_id=%s", getattr(request, "correlation_id", "")
        )
        return error_response(
            request, 500, "ERROR_INTERNO", "Ocurrió un error inesperado"
        )
    if response.status_code == 400:
        return error_response(
            request, 400, "DATOS_INVALIDOS",
            "Los datos enviados no son válidos", errors=response.data,
        )
    if response.status_code == 404:
        return error_response(request, 404, "NO_ENCONTRADO", "El recurso no existe")
    if response.status_code == 405:
        return error_response(
            request, 405, "METODO_NO_PERMITIDO", "Método no permitido en esta ruta"
        )
    return error_response(
        request, response.status_code, "ERROR_INTERNO", "No fue posible atender la petición"
    )