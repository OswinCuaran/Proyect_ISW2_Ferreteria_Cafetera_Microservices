import clients
from flask import Blueprint, jsonify, request
from sqlalchemy import text
from database import engine
from orders import find_order, order_items
from utils import ApiError, Payload, check_id, check_warehouse_access, current_user_id, invalid, iso, number

returns = Blueprint("returns", __name__)

def return_json(connection, return_id):
    row = connection.execute(text("SELECT * FROM product_returns WHERE id = :id"), {"id": return_id}).mappings().first()
    items = connection.execute(text("""
        SELECT product_id, quantity, product_condition FROM product_return_items
        WHERE return_id = :id ORDER BY product_id
    """), {"id": return_id}).mappings().all()
    return {
        "id": row["id"],
        "type": row["type"],
        "order_id": row["order_id"],
        "warehouse_id": row["warehouse_id"],
        "sale_reference": row["sale_reference"],
        "reason": row["reason"],
        "user_id": row["user_id"],
        "items": [{"product_id": i["product_id"], "quantity": number(i["quantity"]), "product_condition": i["product_condition"]} for i in items],
        "created_at": iso(row["created_at"]),
    }

@returns.get("/returns")
def list_returns():
    sql, params = "SELECT id FROM product_returns WHERE 1 = 1", {}
    return_type = request.args.get("type")
    if return_type:
        if return_type not in ("CLIENTE", "PROVEEDOR"):
            raise invalid({"type": ["El parámetro tipo debe ser CLIENTE o PROVEEDOR."]})
        sql += " AND type = :type"
        params["type"] = return_type
    warehouse_id = request.args.get("warehouse_id")
    if warehouse_id:
        if check_id(warehouse_id) is None:
            raise invalid({"warehouse_id": ["El parámetro bodega debe ser un número entero mayor que cero."]})
        sql += " AND warehouse_id = :warehouse_id"
        params["warehouse_id"] = int(warehouse_id)
    sql += " ORDER BY id DESC"
    with engine.connect() as connection:
        ids = connection.execute(text(sql), params).scalars().all()
        result = [return_json(connection, return_id) for return_id in ids]
    return jsonify(result)

@returns.post("/returns")
def create_return():
    payload = Payload()
    return_type = payload.choice("type", "tipo", ["CLIENTE", "PROVEEDOR"])
    warehouse_id = payload.integer("warehouse_id", "bodega")
    order_id = payload.integer("order_id", "orden de compra", required=False)
    sale_reference = payload.string("sale_reference", "referencia de la venta", 50, required=False)
    reason = payload.string("reason", "motivo", 255)
    items = payload.items("items", "productos", "quantity", "cantidad", condition=True)
    if return_type == "PROVEEDOR" and order_id is None and "order_id" not in payload.errors:
        payload.add("order_id", "El campo orden de compra es obligatorio en una devolución a proveedor.")
    payload.check()
    check_warehouse_access(warehouse_id)
    if return_type == "PROVEEDOR":
        with engine.connect() as connection:
            order = find_order(connection, order_id)
            products = {row["product_id"] for row in order_items(connection, order_id)}
        if order["status"] not in ("RECIBIDA_PARCIAL", "RECIBIDA"):
            raise ApiError(409, "ORDEN_SIN_RECEPCION", f"La orden {order['number']} todavía no tiene mercancía recibida")
        errors = {f"items.{i}.product_id": [f"El producto {item['product_id']} no está en la orden {order['number']}."] for i, item in enumerate(items) if item["product_id"] not in products}
        if errors:
            raise invalid(errors)
    else:
        order_id = None
    clients.check_warehouse(warehouse_id)
    clients.require_inventory()
    with engine.begin() as connection:
        return_id = connection.execute(text("""
            INSERT INTO product_returns (type, order_id, warehouse_id, sale_reference, reason, user_id)
            VALUES (:type, :order_id, :warehouse_id, :sale_reference, :reason, :user_id)
        """), {"type": return_type, "order_id": order_id, "warehouse_id": warehouse_id, "sale_reference": sale_reference, "reason": reason, "user_id": current_user_id()}).lastrowid
        connection.execute(text("""
            INSERT INTO product_return_items (return_id, product_id, quantity, product_condition)
            VALUES (:return_id, :product_id, :quantity, :product_condition)
        """), [{**item, "return_id": return_id} for item in items])
        inventory = []
        for item in items:
            movement = {"product_id": item["product_id"], "warehouse_id": warehouse_id,
                        "quantity": float(item["quantity"]), "reference": f"DEV-{return_id}"}
            if return_type == "PROVEEDOR":
                clients.register_movement("exits", {**movement, "type": "DEVOLUCION_PROVEEDOR"})
                action = "SALE_DEL_STOCK"
            elif item["product_condition"] == "BUEN_ESTADO":
                clients.register_movement("entries", {**movement, "type": "DEVOLUCION_CLIENTE"})
                action = "REINGRESA_AL_STOCK"
            else:
                action = "NO_REINGRESA_DEFECTUOSO"
            inventory.append({"product_id": item["product_id"], "action": action})
        data = return_json(connection, return_id)
    data["inventory"] = inventory
    return jsonify({"message": "Devolución registrada correctamente", "return": data}), 201
