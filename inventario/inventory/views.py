import logging
from datetime import datetime, time, timedelta
from functools import wraps
from django.db import transaction
from django.db.models import F, Sum
from django.utils import timezone
from . import services
from .errors import ApiError, Payload, error_response, json_response, query_bool, query_date, query_int
from .models import Movement, Stock, Warehouse
from .serializers import movement_json, number, stock_json, transfer_json, warehouse_json

logger = logging.getLogger("inventario")

def api(*methods):
    def decorator(view):
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            if request.method not in methods:
                return error_response(request, 405, "METODO_NO_PERMITIDO", f"El método {request.method} no está permitido en esta ruta")
            try:
                return view(request, *args, **kwargs)
            except ApiError as error:
                return error_response(request, error.status, error.code, error.message, error.errors)
        return wrapper
    return decorator

@api("GET")
def health(request):
    return json_response({"status": "ok", "service": "inventario"})

def read_warehouse(request):
    payload = Payload(request)
    data = {
        "code": payload.string("code", "código", 10),
        "name": payload.string("name", "nombre", 100),
        "city": payload.string("city", "ciudad", 60),
        "address": payload.string("address", "dirección", 150),
        "phone": payload.string("phone", "teléfono", 20),
        "is_main": payload.boolean("is_main", "bodega principal", default=False),
    }
    payload.check()
    data["code"] = data["code"].upper()
    return data

def find_warehouse(warehouse_id):
    warehouse = Warehouse.objects.filter(id=warehouse_id).first()
    if warehouse is None:
        raise ApiError(404, "NO_ENCONTRADO", f"La bodega {warehouse_id} no existe")
    return warehouse

@api("GET", "POST")
def warehouses(request):
    if request.method == "GET":
        query = Warehouse.objects.all()
        is_active = query_bool(request, "is_active")
        if is_active is not None:
            query = query.filter(is_active=is_active)
        return json_response([warehouse_json(w) for w in query])
    data = read_warehouse(request)
    if Warehouse.objects.filter(code=data["code"]).exists():
        raise ApiError(409, "BODEGA_DUPLICADA", f"Ya existe una bodega con el código {data['code']}")
    with transaction.atomic():
        if data["is_main"]:
            Warehouse.objects.update(is_main=False)
        warehouse = Warehouse.objects.create(**data)
    return json_response({"message": "Bodega creada correctamente", "warehouse": warehouse_json(warehouse)}, status=201)

@api("PUT")
def warehouse_detail(request, warehouse_id):
    warehouse = find_warehouse(warehouse_id)
    data = read_warehouse(request)
    if Warehouse.objects.filter(code=data["code"]).exclude(id=warehouse.id).exists():
        raise ApiError(409, "BODEGA_DUPLICADA", f"Ya existe una bodega con el código {data['code']}")
    with transaction.atomic():
        if data["is_main"]:
            Warehouse.objects.exclude(id=warehouse.id).update(is_main=False)
        for field, value in data.items():
            setattr(warehouse, field, value)
        warehouse.save()
    return json_response({"message": "Bodega actualizada correctamente", "warehouse": warehouse_json(warehouse)})

@api("PATCH")
def deactivate_warehouse(request, warehouse_id):
    warehouse = find_warehouse(warehouse_id)
    total = Stock.objects.filter(warehouse=warehouse).aggregate(total=Sum("quantity"))["total"] or 0
    if total > 0:
        raise ApiError(409, "BODEGA_CON_EXISTENCIAS", f"La {warehouse.name} todavía tiene existencias; trasládelas antes de desactivarla")
    warehouse.is_active = False
    warehouse.save()
    return json_response({"message": "Bodega desactivada correctamente", "warehouse": warehouse_json(warehouse)})

@api("PATCH")
def activate_warehouse(request, warehouse_id):
    warehouse = find_warehouse(warehouse_id)
    warehouse.is_active = True
    warehouse.save()
    return json_response({"message": "Bodega activada correctamente", "warehouse": warehouse_json(warehouse)})

def read_movement(request, types, reason_required=False):
    payload = Payload(request)
    data = {
        "type": payload.choice("type", "tipo", types),
        "product_id": payload.integer("product_id", "producto"),
        "warehouse_id": payload.integer("warehouse_id", "bodega"),
        "quantity": payload.quantity("quantity", "cantidad"),
        "reference": payload.string("reference", "referencia", 50, required=False),
        "reason": payload.string("reason", "motivo", 255, required=reason_required),
    }
    payload.check()
    return data

def register(request, types, message, reason_required=False, check_duplicate=False):
    data = read_movement(request, types, reason_required)
    services.check_warehouse_access(request, data["warehouse_id"])
    warehouse = services.get_active_warehouse(data["warehouse_id"])
    services.check_product(request, data["product_id"])
    if check_duplicate and data["reference"] and Movement.objects.filter(
        reference=data["reference"], product_id=data["product_id"], movement_type__nature="ENTRADA"
    ).exists():
        raise ApiError(409, "MOVIMIENTO_DUPLICADO", f"La referencia {data['reference']} ya se registró para este producto")
    with transaction.atomic():
        movement = services.apply_movement(
            request, data["type"], warehouse, data["product_id"], data["quantity"],
            reference=data["reference"], reason=data["reason"],
        )
    return json_response({"message": message, "movement": movement_json(movement)}, status=201)

@api("POST")
def entries(request):
    return register(request, services.ENTRY_TYPES, "Entrada registrada correctamente", check_duplicate=True)

@api("POST")
def exits(request):
    return register(request, services.EXIT_TYPES, "Salida registrada correctamente")

@api("POST")
def adjustments(request):
    return register(request, services.ADJUSTMENT_TYPES, "Ajuste registrado correctamente", reason_required=True)

@api("GET")
def movements(request):
    product_id = query_int(request, "product_id", "producto", required=True)
    query = Movement.objects.select_related("movement_type").filter(product_id=product_id)
    warehouse_id = query_int(request, "warehouse_id", "bodega")
    if warehouse_id:
        query = query.filter(warehouse_id=warehouse_id)
    date_from = query_date(request, "from", "desde")
    if date_from:
        query = query.filter(created_at__gte=timezone.make_aware(datetime.combine(date_from, time.min)))
    date_to = query_date(request, "to", "hasta")
    if date_to:
        query = query.filter(created_at__lt=timezone.make_aware(datetime.combine(date_to + timedelta(days=1), time.min)))
    query = query.order_by("-created_at", "-id")[:500]
    return json_response([movement_json(m) for m in query])

@api("POST")
def transfers(request):
    payload = Payload(request)
    origin_id = payload.integer("origin_warehouse_id", "bodega de origen")
    destination_id = payload.integer("destination_warehouse_id", "bodega de destino")
    notes = payload.string("notes", "observación", 255, required=False)
    items = payload.items("items", "productos")
    payload.check()
    if origin_id == destination_id:
        raise ApiError(400, "DATOS_INVALIDOS", "La bodega de origen y la de destino deben ser diferentes")
    services.check_warehouse_access(request, origin_id)
    origin = services.get_active_warehouse(origin_id)
    destination = services.get_active_warehouse(destination_id)
    for item in items:
        services.check_product(request, item["product_id"])
    transfer, moves = services.create_transfer(request, origin, destination, items, notes)
    return json_response({"message": "Traslado registrado correctamente", "transfer": transfer_json(transfer, moves)}, status=201)

@api("GET")
def product_stock(request, product_id):
    saved = {s.warehouse_id: s for s in Stock.objects.filter(product_id=product_id)}
    rows = []
    for warehouse in Warehouse.objects.filter(is_active=True):
        stock = saved.get(warehouse.id)
        rows.append({
            "warehouse_id": warehouse.id,
            "warehouse": warehouse.name,
            "quantity": number(stock.quantity) if stock else 0.0,
            "minimum_stock": number(stock.minimum_stock) if stock else 0.0,
        })
    total = sum(row["quantity"] for row in rows)
    return json_response({"product_id": product_id, "total": round(total, 3), "warehouses": rows})

@api("GET")
def below_minimum(request):
    query = Stock.objects.select_related("warehouse").filter(minimum_stock__gt=0, quantity__lt=F("minimum_stock"))
    warehouse_id = query_int(request, "warehouse_id", "bodega")
    if request.headers.get("X-User-Role") == "OPERADOR" and request.headers.get("X-User-Warehouse"):
        warehouse_id = int(request.headers["X-User-Warehouse"])
    if warehouse_id:
        query = query.filter(warehouse_id=warehouse_id)
    query = query.order_by("warehouse_id", "product_id")
    return json_response([stock_json(s) for s in query])

@api("PUT")
def minimum_stock(request, warehouse_id, product_id):
    payload = Payload(request)
    value = payload.quantity("minimum_stock", "stock mínimo", allow_zero=True)
    payload.check()
    warehouse = services.get_active_warehouse(warehouse_id)
    with transaction.atomic():
        stock, _ = Stock.objects.select_for_update().get_or_create(warehouse=warehouse, product_id=product_id)
        stock.minimum_stock = value
        if stock.quantity >= value:
            stock.alert_sent = False
        stock.save()
        if services.needs_alert(stock):
            services.schedule_low_stock_alert(request, warehouse, stock)
    return json_response({"message": "Stock mínimo actualizado correctamente", "stock": stock_json(stock)})

def not_found(request, exception=None):
    return error_response(request, 404, "NO_ENCONTRADO", "La ruta solicitada no existe")

def server_error(request):
    return error_response(request, 500, "ERROR_INTERNO", "Ocurrió un error inesperado en el servicio de inventario")
