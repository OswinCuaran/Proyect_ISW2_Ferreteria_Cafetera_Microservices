from django.urls import include, path

urlpatterns = [
    path("", include("inventory.urls")),
]

handler404 = "inventory.views.not_found"
handler500 = "inventory.views.server_error"
