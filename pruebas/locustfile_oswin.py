import os
import random
import time
import uuid
from datetime import date, timedelta
import requests
from dotenv import load_dotenv
from locust import HttpUser, between, events, task

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
TEST_USERS_PASSWORD = os.getenv("TEST_USERS_PASSWORD", "")
MAIN_WAREHOUSE = 1
SECOND_WAREHOUSE = 2
PRODUCT_CODES = ["LOC-001", "LOC-002", "LOC-003", "LOC-004", "LOC-005"]
SUPPLIER_NIT = "900999999-1"
CATEGORY_NAME = "Pruebas de carga"
STOCK_TARGET = 1000000
RESPONSE_TIME_LIMIT_MS = 2000
REQUIREMENT_NAMES = ["O06 Consultar stock de un producto"]
TEST_USERS = {
    "OPERADOR": {"email": "operador.pruebas@ferreteria.co", "document_number": "9000000001", "first_name": "Operador", "last_name": "Pruebas"},
    "VENDEDOR": {"email": "vendedor.pruebas@ferreteria.co", "document_number": "9000000002", "first_name": "Vendedor", "last_name": "Pruebas"},
}
data = {}

def login(host, email, password):
    for _ in range(3):
        response = requests.post(f"{host}/api/login", json={"email": email, "password": password}, headers={"Accept": "application/json"}, timeout=10)
        if response.status_code == 200:
            return response.json()["token"]
        if response.status_code == 429:
            wait = int(response.headers.get("Retry-After", 60)) + 1
            print(f"El Gateway limitó el inicio de sesión, se espera {wait} s")
            time.sleep(wait)
            continue
        raise RuntimeError(f"No se pudo iniciar sesión con {email}: {response.status_code} {response.text[:200]}")
    raise RuntimeError(f"No se pudo iniciar sesión con {email} después de varios intentos")

def call(host, token, method, path, **kwargs):
    headers = {"Accept": "application/json", "Authorization": f"Bearer {token}"}
    response = requests.request(method, f"{host}/api{path}", headers=headers, timeout=10, **kwargs)
    if response.status_code not in (200, 201):
        raise RuntimeError(f"{method} /api{path} respondió {response.status_code}: {response.text[:200]}")
    return response.json()

def ensure_users(host, admin):
    roles = {role["name"]: role["id"] for role in call(host, admin, "GET", "/roles")}
    question_id = call(host, admin, "GET", "/security-questions")[0]["id"]
    emails = {user["email"] for user in call(host, admin, "GET", "/users")}
    for role, user in TEST_USERS.items():
        if user["email"] not in emails:
            call(host, admin, "POST", "/register", json={
                **user,
                "document_type": "CC",
                "password": TEST_USERS_PASSWORD,
                "role_id": roles[role],
                "warehouse_id": MAIN_WAREHOUSE,
                "security_question_id": question_id,
                "security_answer": "pruebas",
            })

def ensure_supplier(host, admin):
    suppliers = call(host, admin, "GET", "/proveedores", params={"search": SUPPLIER_NIT})
    supplier = next((s for s in suppliers if s["nit"] == SUPPLIER_NIT), None)
    if supplier is None:
        supplier = call(host, admin, "POST", "/proveedores", json={
            "nit": SUPPLIER_NIT,
            "person_type": "JURIDICA",
            "legal_name": "Distribuidora de Pruebas S.A.S",
            "phone": "3009999999",
            "email": "pruebas@distribuidora.co",
            "address": "Calle 1 # 1-1",
            "city": "Manizales",
            "delivery_days": 3,
        })["supplier"]
    return supplier

def ensure_products(host, admin, supplier):
    categories = call(host, admin, "GET", "/catalogo/categories")
    category = next((c for c in categories if c["name"] == CATEGORY_NAME), None)
    if category is None:
        category = call(host, admin, "POST", "/catalogo/categories", json={"name": CATEGORY_NAME})["category"]
    existing = {p["code"]: p for p in call(host, admin, "GET", "/catalogo/products", params={"search": "LOC-"})}
    products = []
    for index, code in enumerate(PRODUCT_CODES, start=1):
        product = existing.get(code)
        if product is None:
            product = call(host, admin, "POST", "/catalogo/products", json={
                "code": code,
                "name": f"Producto de pruebas {index}",
                "category_id": category["id"],
                "supplier_id": supplier["id"],
                "unit_of_measure": "UNIDAD",
                "sale_price": 1000 * index,
            })["product"]
        products.append(product)
    return products

def ensure_stock(host, admin, products):
    for product in products:
        stock = call(host, admin, "GET", f"/inventario/stock/{product['id']}")
        current = next(w["quantity"] for w in stock["warehouses"] if w["warehouse_id"] == MAIN_WAREHOUSE)
        if current < STOCK_TARGET / 2:
            call(host, admin, "POST", "/inventario/movements/adjustments", json={
                "type": "AJUSTE_POSITIVO",
                "product_id": product["id"],
                "warehouse_id": MAIN_WAREHOUSE,
                "quantity": round(STOCK_TARGET - current, 3),
                "reason": "Saldo inicial para las pruebas de carga",
            })

def create_order(host, admin, supplier, products, quantity, send):
    order = call(host, admin, "POST", "/compras/orders", json={
        "supplier_id": supplier["id"],
        "destination_warehouse_id": MAIN_WAREHOUSE,
        "expected_date": (date.today() + timedelta(days=30)).isoformat(),
        "notes": "Orden para las pruebas de carga",
        "items": [{"product_id": product["id"], "quantity_ordered": quantity, "unit_price": 800} for product in products],
    })["order"]
    if send:
        call(host, admin, "PATCH", f"/compras/orders/{order['id']}/status", json={"status": "ENVIADA"})
    return order

def prepare(host):
    admin = login(host, ADMIN_EMAIL, ADMIN_PASSWORD)
    ensure_users(host, admin)
    supplier = ensure_supplier(host, admin)
    products = ensure_products(host, admin, supplier)
    ensure_stock(host, admin, products)
    data["supplier"] = supplier
    data["products"] = products
    data["open_order"] = create_order(host, admin, supplier, products, 900000, send=True)
    data["draft_order"] = create_order(host, admin, supplier, products, 10, send=False)
    data["tokens"] = {
        "ADMINISTRADOR": admin,
        "OPERADOR": login(host, TEST_USERS["OPERADOR"]["email"], TEST_USERS_PASSWORD),
        "VENDEDOR": login(host, TEST_USERS["VENDEDOR"]["email"], TEST_USERS_PASSWORD),
    }

def random_product():
    return random.choice(data["products"])

def auth(role):
    return {"Accept": "application/json", "Authorization": f"Bearer {data['tokens'][role]}"}

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    host = (environment.host or "http://localhost:8000").rstrip("/")
    try:
        if not ADMIN_EMAIL or not ADMIN_PASSWORD or len(TEST_USERS_PASSWORD) < 8:
            raise RuntimeError("Faltan ADMIN_EMAIL, ADMIN_PASSWORD o TEST_USERS_PASSWORD (mínimo 8 caracteres) en pruebas/.env")
        print(f"Preparando los datos de prueba en {host}...")
        prepare(host)
    except (RuntimeError, requests.RequestException) as error:
        print(f"No se pudieron preparar los datos: {error}")
        environment.process_exit_code = 1
        environment.runner.quit()
        return
    print("Datos listos: proveedor, 5 productos con saldo, 2 órdenes de compra y los usuarios Operador y Vendedor")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("\nRequisito REQ-NF-005: el 95 % de las consultas de stock debe responder en menos de 2 segundos")
    for name in REQUIREMENT_NAMES:
        entry = environment.stats.entries.get((name, "GET"))
        if entry is None or entry.num_requests == 0:
            print(f"  {name}: sin peticiones")
            continue
        p95 = entry.get_response_time_percentile(0.95)
        result = "cumple" if p95 < RESPONSE_TIME_LIMIT_MS else "no cumple"
        print(f"  {name}: percentil 95 = {p95:.0f} ms, {result}")

class Vendedor(HttpUser):
    weight = 3
    wait_time = between(1, 3)
    host = "http://localhost:8000"

    def on_start(self):
        self.headers = auth("VENDEDOR")

    @task(5)
    def stock(self):
        product = random_product()
        self.client.get(f"/api/inventario/stock/{product['id']}", headers=self.headers, name="O06 Consultar stock de un producto")

    @task(3)
    def sale(self):
        self.client.post("/api/inventario/movements/exits", headers=self.headers, name="O07 Registrar una venta", json={
            "type": "SALIDA_VENTA_MOSTRADOR",
            "product_id": random_product()["id"],
            "warehouse_id": MAIN_WAREHOUSE,
            "quantity": 1,
        })

    @task(1)
    def me(self):
        self.client.get("/api/me", headers=self.headers, name="O02 Consultar el usuario de la sesión")

    @task(1)
    def forbidden(self):
        with self.client.get("/api/compras/orders", headers=self.headers, name="O04 Ruta sin permiso para el rol", catch_response=True) as response:
            if response.status_code == 403:
                response.success()
            else:
                response.failure(f"Se esperaba 403 y respondió {response.status_code}")

class Operador(HttpUser):
    weight = 2
    wait_time = between(1, 3)
    host = "http://localhost:8000"

    def on_start(self):
        self.headers = auth("OPERADOR")

    @task(2)
    def warehouses(self):
        self.client.get("/api/inventario/warehouses", headers=self.headers, name="O05 Listar bodegas")

    @task(2)
    def entry(self):
        self.client.post("/api/inventario/movements/entries", headers=self.headers, name="O08 Registrar una entrada", json={
            "type": "ENTRADA_COMPRA",
            "product_id": random_product()["id"],
            "warehouse_id": MAIN_WAREHOUSE,
            "quantity": 1,
            "reference": f"PRU-{uuid.uuid4().hex[:12]}",
        })

    @task(2)
    def kardex(self):
        product = random_product()
        self.client.get("/api/inventario/movements", params={"product_id": product["id"]}, headers=self.headers, name="O09 Consultar el kardex de un producto")

    @task(1)
    def transfer(self):
        self.client.post("/api/inventario/transfers", headers=self.headers, name="O10 Trasladar entre bodegas", json={
            "origin_warehouse_id": MAIN_WAREHOUSE,
            "destination_warehouse_id": SECOND_WAREHOUSE,
            "items": [{"product_id": random_product()["id"], "quantity": 1}],
        })

    @task(2)
    def below_minimum(self):
        self.client.get("/api/inventario/stock/below-minimum", headers=self.headers, name="O11 Productos bajo el stock mínimo")

    @task(1)
    def order_detail(self):
        order_id = data["draft_order"]["id"]
        self.client.get(f"/api/compras/orders/{order_id}", headers=self.headers, name="O14 Consultar una orden de compra")

    @task(2)
    def reception(self):
        order_id = data["open_order"]["id"]
        self.client.post(f"/api/compras/orders/{order_id}/receptions", headers=self.headers, name="O15 Registrar la recepción de mercancía", json={
            "items": [{"product_id": random_product()["id"], "quantity_received": 1}],
        })

class Administrador(HttpUser):
    weight = 1
    wait_time = between(1, 3)
    host = "http://localhost:8000"

    def on_start(self):
        self.headers = auth("ADMINISTRADOR")

    @task(1)
    def login(self):
        body = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        with self.client.post("/api/login", json=body, headers={"Accept": "application/json"}, name="O01 Iniciar sesión", catch_response=True) as response:
            if response.status_code in (200, 429):
                response.success()
            else:
                response.failure(f"Respondió {response.status_code}")

    @task(2)
    def users(self):
        self.client.get("/api/users", headers=self.headers, name="O03 Listar usuarios")

    @task(2)
    def orders(self):
        self.client.get("/api/compras/orders", params={"status": "ENVIADA"}, headers=self.headers, name="O12 Listar órdenes enviadas")

    @task(2)
    def create_order(self):
        self.client.post("/api/compras/orders", headers=self.headers, name="O13 Crear una orden de compra", json={
            "supplier_id": data["supplier"]["id"],
            "destination_warehouse_id": MAIN_WAREHOUSE,
            "items": [{"product_id": random_product()["id"], "quantity_ordered": 10, "unit_price": 800}],
        })
