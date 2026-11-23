import logging
import requests
from django.conf import settings
from django.db import transaction
from .errors import ApiError
from .models import Movement, MovementType, Stock, Transfer, Warehouse

logger = logging.getLogger("inventario")

ENTRY_TYPES = ["ENTRADA_COMPRA", "DEVOLUCION_CLIENTE"]
EXIT_TYPES = ["SALIDA_VENTA_MOSTRADOR", "SALIDA_VENTA_MAYORISTA", "DEVOLUCION_PROVEEDOR"]
ADJUSTMENT_TYPES = ["AJUSTE_POSITIVO", "AJUSTE_NEGATIVO"]

def current_user_id(request):
    raw = request.headers.get("X-User-Id", "")
    return int(raw) if raw.isdigit() else 0

def service_headers(request):
    return {
        "X-Internal-Token": settings.INTERNAL_TOKEN,
        "X-Correlation-Id": request.correlation_id,
        "Accept": "application/json",
    }

def check_warehouse_access(request, warehouse_id):
    role = request.headers.get("X-User-Role", "")
    own_warehouse = request.headers.get("X-User-Warehouse", "")
    if role in ("OPERADOR", "VENDEDOR") and own_warehouse and str(warehouse_id) != own_warehouse:
        raise ApiError(403, "BODEGA_NO_PERMITIDA", "Solo puede registrar movimientos en su propia bodega")

def get_active_warehouse(warehouse_id):
    warehouse = Warehouse.objects.filter(id=warehouse_id).first()
    if warehouse is None:
        raise ApiError(404, "NO_ENCONTRADO", f"La bodega {warehouse_id} no existe")
    if not warehouse.is_active:
        raise ApiError(409, "BODEGA_INACTIVA", f"La {warehouse.name} está desactivada")
    return warehouse

def check_product(request, product_id):
    if not settings.CATALOGO_URL:
        return
    try:
        response = requests.get(
            f"{settings.CATALOGO_URL}/products/{product_id}",
            headers=service_headers(request),
            timeout=settings.SERVICE_TIMEOUT,
        )
    except requests.RequestException:
        logger.warning("Catálogo no respondió; el producto %s no se validó correlation_id=%s", product_id, request.correlation_id)
        return
    if response.status_code == 404:
        raise ApiError(404, "PRODUCTO_NO_ENCONTRADO", f"El producto {product_id} no existe en el catálogo")
    if response.ok:
        try:
            data = response.json()
        except ValueError:
            return
        if isinstance(data, dict) and data.get("is_active") is False:
            raise ApiError(409, "PRODUCTO_INACTIVO", f"El producto {product_id} está dado de baja en el catálogo")

def needs_alert(stock):
    return stock.minimum_stock > 0 and stock.quantity < stock.minimum_stock and not stock.alert_sent

def schedule_low_stock_alert(request, warehouse, stock):
    data = {
        "warehouse_id": warehouse.id,
        "warehouse": warehouse.name,
        "product_id": stock.product_id,
        "quantity": float(stock.quantity),
        "minimum_stock": float(stock.minimum_stock),
    }
    headers = service_headers(request)
    transaction.on_commit(lambda: send_low_stock_alert(data, headers))

def send_low_stock_alert(data, headers):
    correlation_id = headers.get("X-Correlation-Id")
    if not settings.NOTIFICACIONES_URL:
        logger.warning("Stock bajo del producto %s en %s, pero no hay NOTIFICACIONES_URL configurada correlation_id=%s", data["product_id"], data["warehouse"], correlation_id)
        return
    try:
        response = requests.post(f"{settings.NOTIFICACIONES_URL}/alerts", json=data, headers=headers, timeout=settings.SERVICE_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException:
        logger.warning("Notificaciones no recibió la alerta de stock bajo del producto %s en %s correlation_id=%s", data["product_id"], data["warehouse"], correlation_id)
        return
    Stock.objects.filter(warehouse_id=data["warehouse_id"], product_id=data["product_id"]).update(alert_sent=True)
    logger.info("Alerta de stock bajo enviada: producto %s en %s correlation_id=%s", data["product_id"], data["warehouse"], correlation_id)

def apply_movement(request, type_code, warehouse, product_id, quantity, reference=None, reason=None, transfer=None):
    movement_type = MovementType.objects.get(code=type_code)
    stock, _ = Stock.objects.select_for_update().get_or_create(warehouse=warehouse, product_id=product_id)
    if movement_type.nature == MovementType.ENTRADA:
        new_quantity = stock.quantity + quantity
    else:
        if stock.quantity < quantity:
            raise ApiError(409, "EXISTENCIAS_INSUFICIENTES", f"Solo hay {stock.quantity:.3f} unidades del producto {product_id} en la {warehouse.name}")
        new_quantity = stock.quantity - quantity
    stock.quantity = new_quantity
    if new_quantity >= stock.minimum_stock:
        stock.alert_sent = False
    stock.save()
    movement = Movement.objects.create(
        movement_type=movement_type,
        warehouse=warehouse,
        product_id=product_id,
        transfer=transfer,
        quantity=quantity,
        resulting_balance=new_quantity,
        reference=reference,
        reason=reason,
        user_id=current_user_id(request),
        correlation_id=request.correlation_id[:36],
    )
    if movement_type.nature == MovementType.SALIDA and needs_alert(stock):
        schedule_low_stock_alert(request, warehouse, stock)
    return movement

def create_transfer(request, origin, destination, items, notes):
    with transaction.atomic():
        transfer = Transfer.objects.create(
            origin_warehouse=origin,
            destination_warehouse=destination,
            user_id=current_user_id(request),
            notes=notes,
        )
        movements = []
        for item in items:
            reference = f"TRA-{transfer.id}"
            movements.append(apply_movement(request, "TRASLADO_SALIDA", origin, item["product_id"],
                                            item["quantity"], reference=reference, transfer=transfer))
            movements.append(apply_movement(request, "TRASLADO_ENTRADA", destination, item["product_id"],
                                            item["quantity"], reference=reference, transfer=transfer))
    return transfer, movements
