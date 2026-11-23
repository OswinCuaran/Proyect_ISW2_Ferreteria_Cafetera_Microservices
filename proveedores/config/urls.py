from django.http import JsonResponse
from django.urls import path

from suppliers import views


def health(request):
    return JsonResponse({"status": "ok", "service": "proveedores"})


def not_found(request, exception=None):
    return JsonResponse({
        "error": "NO_ENCONTRADO",
        "message": "La ruta no existe",
        "correlation_id": getattr(request, "correlation_id", ""),
    }, status=404)


def server_error(request):
    return JsonResponse({
        "error": "ERROR_INTERNO",
        "message": "Ocurrio un error inesperado",
        "correlation_id": getattr(request, "correlation_id", ""),
    }, status=500)


handler404 = not_found
handler500 = server_error

urlpatterns = [
    path("health", health),
    path("", views.supplier_list),
    path("<int:pk>", views.supplier_detail),
    path("<int:pk>/deactivate", views.supplier_deactivate),
    path("<int:pk>/contacts", views.supplier_contacts),
]