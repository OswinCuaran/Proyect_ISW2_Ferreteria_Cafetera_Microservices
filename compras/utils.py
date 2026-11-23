from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from zoneinfo import ZoneInfo
from flask import g, jsonify, request

COLOMBIA = ZoneInfo("America/Bogota")

class ApiError(Exception):
    def __init__(self, status, code, message, errors=None):
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message
        self.errors = errors

def error_response(status, code, message, errors=None):
    body = {"error": code, "message": message}
    if errors:
        body["errors"] = errors
    body["correlation_id"] = g.get("correlation_id")
    return jsonify(body), status

def invalid(errors):
    return ApiError(400, "DATOS_INVALIDOS", "Los datos enviados no son válidos", errors)

def today():
    return datetime.now(COLOMBIA).date()

def number(value):
    return float(value) if value is not None else None

def iso(value):
    return value.isoformat() if value is not None else None

def check_id(value):
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value if value > 0 else None
    if isinstance(value, str) and value.isdigit() and int(value) > 0:
        return int(value)
    return None

def current_user_id():
    raw = request.headers.get("X-User-Id", "")
    return int(raw) if raw.isdigit() else 0

def check_warehouse_access(warehouse_id):
    role = request.headers.get("X-User-Role", "")
    own_warehouse = request.headers.get("X-User-Warehouse", "")
    if role in ("OPERADOR", "VENDEDOR") and own_warehouse and str(warehouse_id) != own_warehouse:
        raise ApiError(403, "BODEGA_NO_PERMITIDA", "Solo puede registrar operaciones de su propia bodega")

class Payload:
    def __init__(self):
        data = request.get_json(silent=True)
        if data is None and request.get_data():
            raise ApiError(400, "DATOS_INVALIDOS", "El cuerpo de la petición no es un JSON válido")
        data = {} if data is None else data
        if not isinstance(data, dict):
            raise ApiError(400, "DATOS_INVALIDOS", "El cuerpo de la petición debe ser un objeto JSON")
        self.data = data
        self.errors = {}
    def add(self, field, message):
        self.errors.setdefault(field, []).append(message)
    def integer(self, field, label, required=True):
        value = self.data.get(field)
        if value is None or value == "":
            if required:
                self.add(field, f"El campo {label} es obligatorio.")
            return None
        result = check_id(value)
        if result is None:
            self.add(field, f"El campo {label} debe ser un número entero mayor que cero.")
        return result
    def string(self, field, label, max_length, required=True):
        value = self.data.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            if required:
                self.add(field, f"El campo {label} es obligatorio.")
            return None
        if not isinstance(value, str):
            self.add(field, f"El campo {label} debe ser un texto.")
            return None
        value = value.strip()
        if len(value) > max_length:
            self.add(field, f"El campo {label} no debe tener más de {max_length} caracteres.")
            return None
        return value
    def choice(self, field, label, options):
        value = self.data.get(field)
        if value is None or value == "":
            self.add(field, f"El campo {label} es obligatorio.")
            return None
        if value not in options:
            self.add(field, f"El campo {label} debe ser uno de: {', '.join(options)}.")
            return None
        return value
    def future_date(self, field, label):
        value = self.data.get(field)
        if value in (None, ""):
            return None
        try:
            result = date.fromisoformat(str(value))
        except ValueError:
            self.add(field, f"El campo {label} debe tener el formato AAAA-MM-DD.")
            return None
        if result < today():
            self.add(field, f"El campo {label} no puede ser anterior a hoy.")
            return None
        return result
    def amount(self, source, field, label, key, allow_zero=False, decimals=3):
        value = source.get(field)
        if value is None or value == "" or isinstance(value, bool):
            self.add(key, f"El campo {label} es obligatorio.")
            return None
        try:
            result = Decimal(str(value))
        except InvalidOperation:
            self.add(key, f"El campo {label} debe ser un número.")
            return None
        if not result.is_finite() or result < 0 or (result == 0 and not allow_zero):
            self.add(key, f"El campo {label} debe ser mayor {'o igual a' if allow_zero else 'que'} cero.")
            return None
        if result.as_tuple().exponent < -decimals:
            self.add(key, f"El campo {label} no puede tener más de {decimals} decimales.")
            return None
        if result >= Decimal("1000000000"):
            self.add(key, f"El campo {label} es demasiado grande.")
            return None
        return result
    def items(self, field, label, quantity_field, quantity_label, price=False, condition=False):
        value = self.data.get(field)
        if not isinstance(value, list) or not value:
            self.add(field, f"El campo {label} debe ser una lista con al menos un producto.")
            return []
        result, seen = [], set()
        for index, item in enumerate(value):
            key = f"{field}.{index}"
            if not isinstance(item, dict):
                self.add(key, "Cada producto debe ser un objeto JSON.")
                continue
            ok = True
            product_id = check_id(item.get("product_id"))
            if product_id is None:
                self.add(f"{key}.product_id", "El campo producto debe ser un número entero mayor que cero.")
                ok = False
            elif product_id in seen:
                self.add(f"{key}.product_id", f"El producto {product_id} está repetido en la lista.")
                ok = False
            else:
                seen.add(product_id)
            row = {"product_id": product_id, quantity_field: self.amount(item, quantity_field, quantity_label, f"{key}.{quantity_field}")}
            ok = ok and row[quantity_field] is not None
            if price:
                row["unit_price"] = self.amount(item, "unit_price", "precio unitario", f"{key}.unit_price",allow_zero=True, decimals=2)
                ok = ok and row["unit_price"] is not None
            if condition:
                row["product_condition"] = item.get("product_condition")
                if row["product_condition"] not in ("BUEN_ESTADO", "DEFECTUOSO"):
                    self.add(f"{key}.product_condition", "El campo estado del producto debe ser BUEN_ESTADO o DEFECTUOSO.")
                    ok = False
            if ok:
                result.append(row)
        return result
    def check(self):
        if self.errors:
            raise invalid(self.errors)
