def number(value):
    return float(value) if value is not None else None

def warehouse_json(warehouse):
    return {
        "id": warehouse.id,
        "code": warehouse.code,
        "name": warehouse.name,
        "city": warehouse.city,
        "address": warehouse.address,
        "phone": warehouse.phone,
        "is_main": warehouse.is_main,
        "is_active": warehouse.is_active,
    }

def movement_json(movement):
    return {
        "id": movement.id,
        "type": movement.movement_type.code,
        "product_id": movement.product_id,
        "warehouse_id": movement.warehouse_id,
        "quantity": number(movement.quantity),
        "resulting_balance": number(movement.resulting_balance),
        "transfer_id": movement.transfer_id,
        "reference": movement.reference,
        "reason": movement.reason,
        "user_id": movement.user_id,
        "created_at": movement.created_at.isoformat(),
    }

def stock_json(stock):
    return {
        "warehouse_id": stock.warehouse_id,
        "warehouse": stock.warehouse.name,
        "product_id": stock.product_id,
        "quantity": number(stock.quantity),
        "minimum_stock": number(stock.minimum_stock),
        "alert_sent": stock.alert_sent,
    }

def transfer_json(transfer, movements):
    return {
        "id": transfer.id,
        "origin_warehouse_id": transfer.origin_warehouse_id,
        "destination_warehouse_id": transfer.destination_warehouse_id,
        "notes": transfer.notes,
        "user_id": transfer.user_id,
        "movements": [movement_json(m) for m in movements],
        "created_at": transfer.created_at.isoformat(),
    }
