import logging, requests
from flask import g, request
from database import INTERNAL_TOKEN, INVENTARIO_URL, PROVEEDORES_URL, SERVICE_TIMEOUT
from utils import ApiError

logger = logging.getLogger("compras")

def service_headers():
    return {
        "X-Internal-Token": INTERNAL_TOKEN,
        "X-Correlation-Id": g.correlation_id,
        "X-User-Id": request.headers.get("X-User-Id", ""),
        "X-User-Role": request.headers.get("X-User-Role", ""),
        "X-User-Warehouse": request.headers.get("X-User-Warehouse", ""),
        "Accept": "application/json",
    }

def check_supplier(supplier_id):
    if not PROVEEDORES_URL:
        return
    try:
        response = requests.get(f"{PROVEEDORES_URL}/{supplier_id}", headers=service_headers(), timeout=SERVICE_TIMEOUT)
    except requests.RequestException:
        logger.warning("Proveedores no respondió; el proveedor %s no se validó correlation_id=%s", supplier_id, g.correlation_id)
        return
    if response.status_code == 404:
        raise ApiError(404, "PROVEEDOR_NO_ENCONTRADO", f"El proveedor {supplier_id} no existe")
    try:
        supplier = response.json() if response.ok else {}
    except ValueError:
        supplier = {}
    if supplier.get("is_active") is False:
        raise ApiError(409, "PROVEEDOR_INACTIVO", f"El proveedor {supplier_id} está dado de baja")

def check_warehouse(warehouse_id):
    if not INVENTARIO_URL:
        return
    try:
        response = requests.get(f"{INVENTARIO_URL}/warehouses", headers=service_headers(), timeout=SERVICE_TIMEOUT)
        warehouses = response.json() if response.ok else None
    except (requests.RequestException, ValueError):
        logger.warning("Inventario no respondió; la bodega %s no se validó correlation_id=%s", warehouse_id, g.correlation_id)
        return
    if isinstance(warehouses, list):
        match = next((w for w in warehouses if w.get("id") == warehouse_id), None)
        if match is None:
            raise ApiError(404, "BODEGA_NO_ENCONTRADA", f"La bodega {warehouse_id} no existe")
        if match.get("is_active") is False:
            raise ApiError(409, "BODEGA_INACTIVA", f"La {match.get('name')} está desactivada")

def require_inventory():
    if not INVENTARIO_URL:
        raise ApiError(503, "SERVICIO_NO_DISPONIBLE", "No hay INVENTARIO_URL configurada en Compras")
    try:
        requests.get(f"{INVENTARIO_URL}/health", timeout=SERVICE_TIMEOUT).raise_for_status()
    except requests.RequestException:
        raise ApiError(503, "SERVICIO_NO_DISPONIBLE", "Inventario no está disponible; no se registró nada")

def register_movement(kind, movement):
    try:
        response = requests.post(f"{INVENTARIO_URL}/movements/{kind}", json=movement, headers=service_headers(), timeout=SERVICE_TIMEOUT)
    except requests.RequestException:
        raise ApiError(503, "SERVICIO_NO_DISPONIBLE", "Inventario dejó de responder; no se registró nada")
    if response.status_code == 201:
        return response.json().get("movement")
    try:
        body = response.json()
    except ValueError:
        body = {}
    if body.get("error") == "MOVIMIENTO_DUPLICADO":
        return None
    raise ApiError(response.status_code, body.get("error", "ERROR_INVENTARIO"), body.get("message", "Inventario rechazó el movimiento"), body.get("errors"))
