import clients
from uuid import uuid4
from flask import Blueprint, jsonify, request
from sqlalchemy import text
from database import engine
from utils import (ApiError, Payload, check_id, check_warehouse_access, current_user_id, invalid, iso, number, today)

orders = Blueprint("orders", __name__)
STATUSES = ["BORRADOR", "ENVIADA", "RECIBIDA_PARCIAL", "RECIBIDA", "CANCELADA"]
TRANSITIONS = {
    "BORRADOR": ["ENVIADA", "CANCELADA"],
    "ENVIADA": ["CANCELADA"],
    "RECIBIDA_PARCIAL": ["CANCELADA"],
    "RECIBIDA": [],
    "CANCELADA": [],
}

def find_order(connection, order_id, lock=False):
    sql = "SELECT * FROM purchase_orders WHERE id = :id" + (" FOR UPDATE" if lock else "")
    order = connection.execute(text(sql), {"id": order_id}).mappings().first()
    if order is None:
        raise ApiError(404, "NO_ENCONTRADO", f"La orden de compra {order_id} no existe")
    return order

def order_items(connection, order_id):
    return connection.execute(text("""
        SELECT i.product_id, i.quantity_ordered, i.unit_price, COALESCE(SUM(ri.quantity_received), 0) AS quantity_received
        FROM purchase_order_items i
        LEFT JOIN receptions r ON r.order_id = i.order_id
        LEFT JOIN reception_items ri ON ri.reception_id = r.id AND ri.product_id = i.product_id
        WHERE i.order_id = :order_id
        GROUP BY i.product_id, i.quantity_ordered, i.unit_price
        ORDER BY i.product_id
    """), {"order_id": order_id}).mappings().all()

def order_json(order, items):
    lines, total = [], 0
    for item in items:
        subtotal = item["quantity_ordered"] * item["unit_price"]
        total += subtotal
        lines.append({
            "product_id": item["product_id"],
            "quantity_ordered": number(item["quantity_ordered"]),
            "quantity_received": number(item["quantity_received"]),
            "quantity_pending": number(item["quantity_ordered"] - item["quantity_received"]),
            "unit_price": number(item["unit_price"]),
            "subtotal": number(subtotal),
        })
    return {
        "id": order["id"],
        "number": order["number"],
        "supplier_id": order["supplier_id"],
        "destination_warehouse_id": order["destination_warehouse_id"],
        "status": order["status"],
        "issue_date": iso(order["issue_date"]),
        "expected_date": iso(order["expected_date"]),
        "notes": order["notes"],
        "user_id": order["user_id"],
        "items": lines,
        "total": round(float(total), 2),
        "created_at": iso(order["created_at"]),
    }

def reception_json(connection, reception_id):
    reception = connection.execute(text("SELECT * FROM receptions WHERE id = :id"), {"id": reception_id}).mappings().first()
    items = connection.execute(text(
        "SELECT product_id, quantity_received FROM reception_items WHERE reception_id = :id ORDER BY product_id"
    ), {"id": reception_id}).mappings().all()
    return {
        "id": reception["id"],
        "order_id": reception["order_id"],
        "user_id": reception["user_id"],
        "notes": reception["notes"],
        "items": [{"product_id": i["product_id"], "quantity_received": number(i["quantity_received"])} for i in items],
        "created_at": iso(reception["created_at"]),
    }

def full_order(connection, order_id):
    data = order_json(find_order(connection, order_id), order_items(connection, order_id))
    ids = connection.execute(text("SELECT id FROM receptions WHERE order_id = :id ORDER BY id"), {"id": order_id}).scalars().all()
    data["receptions"] = [reception_json(connection, reception_id) for reception_id in ids]
    return data

@orders.get("/orders")
def list_orders():
    sql, params = "SELECT * FROM purchase_orders WHERE 1 = 1", {}
    status = request.args.get("status")
    if status:
        if status not in STATUSES:
            raise invalid({"status": [f"El parámetro estado debe ser uno de: {', '.join(STATUSES)}."]})
        sql += " AND status = :status"
        params["status"] = status
    supplier_id = request.args.get("supplier_id")
    if supplier_id:
        if check_id(supplier_id) is None:
            raise invalid({"supplier_id": ["El parámetro proveedor debe ser un número entero mayor que cero."]})
        sql += " AND supplier_id = :supplier_id"
        params["supplier_id"] = int(supplier_id)
    sql += " ORDER BY id DESC"
    with engine.connect() as connection:
        rows = connection.execute(text(sql), params).mappings().all()
        result = [order_json(row, order_items(connection, row["id"])) for row in rows]
    return jsonify(result)

@orders.post("/orders")
def create_order():
    payload = Payload()
    supplier_id = payload.integer("supplier_id", "proveedor")
    warehouse_id = payload.integer("destination_warehouse_id", "bodega de destino")
    expected_date = payload.future_date("expected_date", "fecha esperada")
    notes = payload.string("notes", "observación", 255, required=False)
    items = payload.items("items", "productos", "quantity_ordered", "cantidad pedida", price=True)
    payload.check()
    clients.check_supplier(supplier_id)
    clients.check_warehouse(warehouse_id)
    issue_date = today()
    with engine.begin() as connection:
        result = connection.execute(text("""
            INSERT INTO purchase_orders
            (number, supplier_id, destination_warehouse_id, user_id, issue_date, expected_date, notes)
            VALUES (:number, :supplier_id, :warehouse_id, :user_id, :issue_date, :expected_date, :notes)
        """), {
            "number": f"TMP-{uuid4().hex[:16]}",
            "supplier_id": supplier_id,
            "warehouse_id": warehouse_id,
            "user_id": current_user_id(),
            "issue_date": issue_date,
            "expected_date": expected_date,
            "notes": notes,
        })
        order_id = result.lastrowid
        connection.execute(text("UPDATE purchase_orders SET number = :number WHERE id = :id"), {"number": f"OC-{issue_date.year}-{order_id:04d}", "id": order_id})
        connection.execute(text("""
            INSERT INTO purchase_order_items (order_id, product_id, quantity_ordered, unit_price)
            VALUES (:order_id, :product_id, :quantity_ordered, :unit_price)
        """), [{**item, "order_id": order_id} for item in items])
        data = full_order(connection, order_id)
    return jsonify({"message": "Orden de compra creada correctamente", "order": data}), 201

@orders.get("/orders/<int:order_id>")
def get_order(order_id):
    with engine.connect() as connection:
        data = full_order(connection, order_id)
    return jsonify(data)

@orders.patch("/orders/<int:order_id>/status")
def change_status(order_id):
    payload = Payload()
    status = payload.choice("status", "estado", ["ENVIADA", "CANCELADA"])
    payload.check()
    with engine.begin() as connection:
        order = find_order(connection, order_id, lock=True)
        if status not in TRANSITIONS[order["status"]]:
            raise ApiError(409, "TRANSICION_INVALIDA", f"Una orden {order['status']} no puede pasar a {status}")
        connection.execute(text("UPDATE purchase_orders SET status = :status WHERE id = :id"), {"status": status, "id": order_id})
        data = full_order(connection, order_id)
    message = "Orden enviada al proveedor" if status == "ENVIADA" else "Orden cancelada"
    return jsonify({"message": message, "order": data})

@orders.post("/orders/<int:order_id>/receptions")
def create_reception(order_id):
    payload = Payload()
    notes = payload.string("notes", "observación", 255, required=False)
    items = payload.items("items", "productos", "quantity_received", "cantidad recibida")
    payload.check()
    with engine.connect() as connection:
        order = find_order(connection, order_id)
    check_warehouse_access(order["destination_warehouse_id"])
    clients.require_inventory()
    with engine.begin() as connection:
        order = find_order(connection, order_id, lock=True)
        if order["status"] not in ("ENVIADA", "RECIBIDA_PARCIAL"):
            raise ApiError(409, "ORDEN_NO_ENVIADA", f"Solo se recibe mercancía de órdenes ENVIADA o RECIBIDA_PARCIAL; la {order['number']} está {order['status']}")
        pending = {row["product_id"]: row["quantity_ordered"] - row["quantity_received"] for row in order_items(connection, order_id)}
        errors = {f"items.{i}.product_id": [f"El producto {item['product_id']} no está en la orden {order['number']}."] for i, item in enumerate(items) if item["product_id"] not in pending}
        if errors:
            raise invalid(errors)
        for item in items:
            if item["quantity_received"] > pending[item["product_id"]]:
                raise ApiError(409, "CANTIDAD_EXCEDE_PENDIENTE", f"Del producto {item['product_id']} solo faltan {pending[item['product_id']]:.3f} unidades por recibir")
        reception_id = connection.execute(text("""
            INSERT INTO receptions (order_id, user_id, notes) VALUES (:order_id, :user_id, :notes)
        """), {"order_id": order_id, "user_id": current_user_id(), "notes": notes}).lastrowid
        connection.execute(text("""
            INSERT INTO reception_items (reception_id, product_id, quantity_received)
            VALUES (:reception_id, :product_id, :quantity_received)
        """), [{**item, "reception_id": reception_id} for item in items])
        for item in items:
            clients.register_movement("entries", {
                "type": "ENTRADA_COMPRA",
                "product_id": item["product_id"],
                "warehouse_id": order["destination_warehouse_id"],
                "quantity": float(item["quantity_received"]),
                "reference": f"REC-{reception_id}",
            })
        for item in items:
            pending[item["product_id"]] -= item["quantity_received"]
        new_status = "RECIBIDA" if all(quantity <= 0 for quantity in pending.values()) else "RECIBIDA_PARCIAL"
        connection.execute(text("UPDATE purchase_orders SET status = :status WHERE id = :id"), {"status": new_status, "id": order_id})
        reception = reception_json(connection, reception_id)
    return jsonify({"message": "Recepción registrada correctamente", "order_status": new_status,
                    "reception": reception}), 201
