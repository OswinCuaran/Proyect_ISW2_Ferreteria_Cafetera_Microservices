import math
from datetime import date, datetime, timedelta, timezone
from flask import Blueprint, g, jsonify, request
from clients import collect_stock, sales_units
from errors import InvalidData

bp = Blueprint("reports", __name__)

LEAD_TIME_DAYS = 7
COVERAGE_DAYS = 30
ALERT_DAYS = 15
HISTORY_DAYS = 30

def int_param(name):
    value = request.args.get(name)
    if value is None:
        return None
    try:
        number = int(value)
        if number < 1:
            raise ValueError
        return number
    except ValueError:
        raise InvalidData(f"{name} debe ser un entero positivo")

def date_param(name):
    value = request.args.get(name)
    if not value:
        raise InvalidData(f"{name} es obligatorio (formato AAAA-MM-DD)")
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise InvalidData(f"{name} debe tener formato AAAA-MM-DD")

def today_utc():
    return datetime.now(timezone.utc).date()

def season_for(day):
    if (day.month == 11 and day.day >= 15) or day.month == 12 or (day.month == 1 and day.day <= 15):
        return "Fin de año", 1.3
    return None, 1.0

def rotation_by_product(rows, sold):
    products = {}
    for row in rows:
        item = products.setdefault(row["product_id"], {
            "product_id": row["product_id"], "name": row["name"], "units_sold": 0, "current": 0})
        item["units_sold"] += sold.get((row["product_id"], row["warehouse_id"]), 0)
        item["current"] += row["quantity"]
    result = []
    for item in products.values():
        average = item["current"] + item["units_sold"] / 2
        result.append({
            "product_id": item["product_id"],
            "name": item["name"],
            "units_sold": item["units_sold"],
            "average_stock": round(average, 2),
            "rotation_index": round(item["units_sold"] / average, 2) if average > 0 else 0,
        })
    return result

@bp.get("/stock")
def stock():
    rows = collect_stock(g.correlation_id, int_param("warehouse_id"), int_param("category_id"))
    result = [
        {key: row[key] for key in ("product_id", "code", "name", "category", "warehouse_id", "warehouse", "quantity", "minimum_stock")}
        for row in rows
    ]
    return jsonify(result)

@bp.get("/valuation")
def valuation():
    rows = collect_stock(g.correlation_id, int_param("warehouse_id"))
    by_warehouse = {}
    by_product = {}
    for row in rows:
        value = row["quantity"] * row["unit_price"]
        wh = by_warehouse.setdefault(row["warehouse_id"], {
            "warehouse_id": row["warehouse_id"], "warehouse": row["warehouse"], "value": 0})
        wh["value"] += value
        pr = by_product.setdefault(row["product_id"], {
            "product_id": row["product_id"], "name": row["name"],
            "quantity": 0, "unit_price": row["unit_price"], "value": 0})
        pr["quantity"] += row["quantity"]
        pr["value"] += value
    for item in list(by_warehouse.values()) + list(by_product.values()):
        item["value"] = round(item["value"], 2)
    return jsonify({
        "total_value": round(sum(w["value"] for w in by_warehouse.values()), 2),
        "by_warehouse": list(by_warehouse.values()),
        "products": list(by_product.values()),
    })

@bp.get("/rotation")
def rotation():
    date_from, date_to = date_param("from"), date_param("to")
    if date_from > date_to:
        raise InvalidData("from no puede ser posterior a to")
    limit = int_param("limit") or 5
    rows = collect_stock(g.correlation_id, int_param("warehouse_id"))
    sold = sales_units(sorted({r["product_id"] for r in rows}), date_from, date_to, g.correlation_id)
    items = rotation_by_product(rows, sold)
    highest = sorted([i for i in items if i["units_sold"] > 0], key=lambda i: i["rotation_index"], reverse=True)[:limit]
    lowest = sorted(items, key=lambda i: i["rotation_index"])[:limit]
    return jsonify({"highest_rotation": highest, "lowest_rotation": lowest})

@bp.get("/suggestions")
def suggestions():
    today = today_utc()
    rows = collect_stock(g.correlation_id, int_param("warehouse_id"))
    sold = sales_units(sorted({r["product_id"] for r in rows}), today - timedelta(days=HISTORY_DAYS), today, g.correlation_id)
    season, factor = season_for(today)
    result = []
    for row in rows:
        units = sold.get((row["product_id"], row["warehouse_id"]), 0)
        daily_demand = units / HISTORY_DAYS * factor
        quantity = row["quantity"]
        if daily_demand > 0:
            days_left = quantity / daily_demand
            if days_left > ALERT_DAYS:
                continue
            suggested = math.ceil(daily_demand * COVERAGE_DAYS - quantity)
            order_in_days = max(int(days_left) - LEAD_TIME_DAYS, 0)
        elif row["minimum_stock"] > 0 and quantity < row["minimum_stock"]:
            suggested = math.ceil(row["minimum_stock"] * 2 - quantity)
            order_in_days = 0
        else:
            continue
        if suggested > 0:
            result.append({
                "product_id": row["product_id"],
                "name": row["name"],
                "warehouse_id": row["warehouse_id"],
                "suggested_quantity": suggested,
                "suggested_date": (today + timedelta(days=order_in_days)).isoformat(),
                "season": season,
            })
    return jsonify(result)

@bp.get("/dashboard")
def dashboard():
    today = today_utc()
    rows = collect_stock(g.correlation_id)
    sold = sales_units(sorted({r["product_id"] for r in rows}), today - timedelta(days=HISTORY_DAYS), today, g.correlation_id)
    totals = {}
    for row in rows:
        totals[row["product_id"]] = totals.get(row["product_id"], 0) + row["quantity"]
    items = rotation_by_product(rows, sold)
    return jsonify({
        "total_inventory_value": round(sum(r["quantity"] * r["unit_price"] for r in rows), 2),
        "products_out_of_stock": sum(1 for q in totals.values() if q == 0),
        "products_below_minimum": len({r["product_id"] for r in rows if r["minimum_stock"] > 0 and r["quantity"] < r["minimum_stock"]}),
        "average_rotation": round(sum(i["rotation_index"] for i in items) / len(items), 2) if items else 0,
        "calculated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    })