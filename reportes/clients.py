import logging
import os
from concurrent.futures import ThreadPoolExecutor
import requests
from errors import ServiceUnavailable
from datetime import datetime

logger = logging.getLogger("reportes")

def _get(service, env_name, path, correlation_id, params=None):
    """Llama a otro servicio con el token interno y 2 s de espera máxima."""
    url = f"{os.getenv(env_name, '')}{path}"
    try:
        response = requests.get(
            url,
            params=params,
            headers={
                "X-Internal-Token": os.getenv("INTERNAL_TOKEN", ""),
                "X-Correlation-Id": correlation_id,
            },
            timeout=2,
        )
    except requests.RequestException as err:
        logger.error("ERROR llamando a %s correlation_id=%s: %s", service, correlation_id, err)
        raise ServiceUnavailable(service)
    if response.status_code != 200:
        logger.error("ERROR %s respondió %s en %s correlation_id=%s",
                     service, response.status_code, path, correlation_id)
        raise ServiceUnavailable(service)
    return response.json()

def get_products(correlation_id):
    return _get("catalogo", "CATALOGO_URL", "/products", correlation_id)

def get_stock(product_id, correlation_id):
    return _get("inventario", "INVENTARIO_URL", f"/stock/{product_id}", correlation_id)

def collect_stock(correlation_id, warehouse_id=None, category_id=None):
    """Una fila por producto y bodega, con el precio del producto."""
    products = [p for p in get_products(correlation_id) if p.get("is_active", True)]
    if category_id is not None:
        products = [p for p in products if p.get("category_id") == category_id]

    # Se consulta el stock de varios productos a la vez
    with ThreadPoolExecutor(max_workers=8) as pool:
        stocks = list(pool.map(lambda p: get_stock(p["id"], correlation_id), products))

    rows = []
    for product, stock in zip(products, stocks):
        for wh in stock["warehouses"]:
            if warehouse_id is not None and wh["warehouse_id"] != warehouse_id:
                continue
            rows.append({
                "product_id": product["id"],
                "code": product["code"],
                "name": product["name"],
                "category": product.get("category"),
                "unit_price": product["sale_price"],
                "warehouse_id": wh["warehouse_id"],
                "warehouse": wh["warehouse"],
                "quantity": wh["quantity"],
                "minimum_stock": wh["minimum_stock"],
            })
    return rows

def get_movements(product_id, correlation_id):
    data = _get("inventario", "INVENTARIO_URL", "/movements", correlation_id,
                params={"product_id": product_id})
    if isinstance(data, dict):
        data = data.get("results") or data.get("data") or []
    return data

def sales_units(product_ids, date_from, date_to, correlation_id):
    """Unidades vendidas por (producto, bodega) entre dos fechas, ambas incluidas."""
    with ThreadPoolExecutor(max_workers=8) as pool:
        movement_lists = list(pool.map(lambda pid: get_movements(pid, correlation_id), product_ids))

    sold = {}
    for movements in movement_lists:
        for movement in movements:
            if not movement["type"].startswith("SALIDA_VENTA"):
                continue
            day = datetime.fromisoformat(movement["created_at"]).date()
            if date_from <= day <= date_to:
                key = (movement["product_id"], movement["warehouse_id"])
                sold[key] = sold.get(key, 0) + movement["quantity"]
    return sold