import json
from datetime import date
from decimal import Decimal, InvalidOperation

from django.http import JsonResponse

class ApiError(Exception):
    def __init__(self, status, code, message, errors=None):
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message
        self.errors = errors

def json_response(data, status=200):
    return JsonResponse(data, status=status, safe=False, json_dumps_params={"ensure_ascii": False})

def error_response(request, status, code, message, errors=None):
    body = {"error": code, "message": message}
    if errors:
        body["errors"] = errors
    body["correlation_id"] = getattr(request, "correlation_id", None)
    return json_response(body, status=status)

def invalid(errors):
    return ApiError(400, "DATOS_INVALIDOS", "Los datos enviados no son válidos", errors)

def to_decimal(value):
    if isinstance(value, bool) or value is None:
        return None
    try:
        number = Decimal(str(value))
    except InvalidOperation:
        return None
    return number if number.is_finite() else None

class Payload:
    def __init__(self, request):
        try:
            self.data = json.loads(request.body or b"{}")
        except (json.JSONDecodeError, UnicodeDecodeError):
            raise ApiError(400, "DATOS_INVALIDOS", "El cuerpo de la petición no es un JSON válido")
        if not isinstance(self.data, dict):
            raise ApiError(400, "DATOS_INVALIDOS", "El cuerpo de la petición debe ser un objeto JSON")
        self.errors = {}
    def add(self, field, message):
        self.errors.setdefault(field, []).append(message)
    def missing(self, field, label):
        value = self.data.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            self.add(field, f"El campo {label} es obligatorio.")
            return True
        return False
    def string(self, field, label, max_length, required=True):
        if field not in self.data or self.data.get(field) in (None, ""):
            if required:
                self.add(field, f"El campo {label} es obligatorio.")
            return None
        value = self.data[field]
        if not isinstance(value, str):
            self.add(field, f"El campo {label} debe ser un texto.")
            return None
        value = value.strip()
        if required and not value:
            self.add(field, f"El campo {label} es obligatorio.")
            return None
        if len(value) > max_length:
            self.add(field, f"El campo {label} no debe tener más de {max_length} caracteres.")
            return None
        return value or None
    def integer(self, field, label):
        if self.missing(field, label):
            return None
        value = check_id(self.data[field])
        if value is None:
            self.add(field, f"El campo {label} debe ser un número entero mayor que cero.")
        return value
    def quantity(self, field, label, allow_zero=False, data=None, error_key=None):
        source = self.data if data is None else data
        key = error_key or field
        value = source.get(field)
        if value is None or value == "":
            self.add(key, f"El campo {label} es obligatorio.")
            return None
        number = to_decimal(value)
        if number is None:
            self.add(key, f"El campo {label} debe ser un número.")
            return None
        if number < 0 or (number == 0 and not allow_zero):
            self.add(key, f"El campo {label} debe ser mayor {'o igual a' if allow_zero else 'que'} cero.")
            return None
        if number.as_tuple().exponent < -3:
            self.add(key, f"El campo {label} no puede tener más de 3 decimales.")
            return None
        if number >= Decimal("1000000000"):
            self.add(key, f"El campo {label} es demasiado grande.")
            return None
        return number
    def boolean(self, field, label, default=False):
        value = self.data.get(field, default)
        if not isinstance(value, bool):
            self.add(field, f"El campo {label} debe ser verdadero o falso.")
            return default
        return value
    def choice(self, field, label, options):
        if self.missing(field, label):
            return None
        value = self.data[field]
        if value not in options:
            self.add(field, f"El campo {label} debe ser uno de: {', '.join(options)}.")
            return None
        return value
    def items(self, field, label):
        value = self.data.get(field)
        if not isinstance(value, list) or not value:
            self.add(field, f"El campo {label} debe ser una lista con al menos un producto.")
            return []
        result = []
        for index, item in enumerate(value):
            if not isinstance(item, dict):
                self.add(f"{field}.{index}", "Cada producto debe tener product_id y quantity.")
                continue
            product_id = check_id(item.get("product_id"))
            if product_id is None:
                self.add(f"{field}.{index}.product_id", "El campo producto debe ser un número entero mayor que cero.")
            quantity = self.quantity("quantity", "cantidad", data=item, error_key=f"{field}.{index}.quantity")
            if product_id is not None and quantity is not None:
                result.append({"product_id": product_id, "quantity": quantity})
        return result
    def check(self):
        if self.errors:
            raise invalid(self.errors)

def check_id(value):
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value if value > 0 else None
    if isinstance(value, str) and value.isdigit():
        return int(value) if int(value) > 0 else None
    return None

def query_int(request, name, label, required=False):
    raw = request.GET.get(name)
    if raw in (None, ""):
        if required:
            raise invalid({name: [f"El parámetro {label} es obligatorio."]})
        return None
    value = check_id(raw)
    if value is None:
        raise invalid({name: [f"El parámetro {label} debe ser un número entero mayor que cero."]})
    return value

def query_date(request, name, label):
    raw = request.GET.get(name)
    if raw in (None, ""):
        return None
    try:
        return date.fromisoformat(raw)
    except ValueError:
        raise invalid({name: [f"El parámetro {label} debe tener el formato AAAA-MM-DD."]})

def query_bool(request, name):
    raw = request.GET.get(name)
    if raw is None:
        return None
    return raw.lower() in ("1", "true", "si", "sí")
