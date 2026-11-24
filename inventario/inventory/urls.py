from django.urls import path

from . import views

urlpatterns = [
    path("health", views.health),
    path("warehouses", views.warehouses),
    path("warehouses/<int:warehouse_id>", views.warehouse_detail),
    path("warehouses/<int:warehouse_id>/deactivate", views.deactivate_warehouse),
    path("warehouses/<int:warehouse_id>/activate", views.activate_warehouse),
    path("movements", views.movements),
    path("movements/entries", views.entries),
    path("movements/exits", views.exits),
    path("movements/adjustments", views.adjustments),
    path("transfers", views.transfers),
    path("stock/below-minimum", views.below_minimum),
    path("stock/<int:warehouse_id>/<int:product_id>/minimum", views.minimum_stock),
    path("stock/<int:product_id>", views.product_stock),
]
