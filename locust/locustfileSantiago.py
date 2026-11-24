import os
import uuid
import requests
from locust import HttpUser, LoadTestShape, between, events, tag, task

INTERNAL_TOKEN = os.getenv("INTERNAL_TOKEN", "")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@ferreteriacafetera.co")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
CATALOGO_DIRECT = os.getenv("CATALOGO_DIRECT", "http://localhost:3001")
NOTIFICACIONES_DIRECT = os.getenv("NOTIFICACIONES_DIRECT", "http://localhost:3002")
SHAPE = os.getenv("SHAPE", "load")   # load, stress o spike
USER_TOKEN = None

@events.test_start.add_listener
def login_once(environment, **kwargs):
    """El login permite 10 por minuto: se hace una vez y se comparte el token."""
    global USER_TOKEN
    response = requests.post(
        f"{environment.host}/api/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        timeout=5,
    )
    response.raise_for_status()
    USER_TOKEN = response.json()["token"]

@events.quitting.add_listener
def check_criteria(environment, **kwargs):
    """En las pruebas de carga: falla si hay errores o el p95 supera 2 s."""
    total = environment.stats.total
    if SHAPE == "load" and (total.fail_ratio > 0 or total.get_response_time_percentile(0.95) > 2000):
        environment.process_exit_code = 1

class Shape(LoadTestShape):
    """La forma de la carga cambia según la variable SHAPE."""
    def tick(self):
        t = self.get_run_time()
        if SHAPE == "load":                       # 50 usuarios constantes, 45 s
            return (50, 10) if t < 45 else None
        if SHAPE == "stress":                     # +25 usuarios cada 15 s, hasta 150
            if t >= 90:
                return None
            return (25 * (int(t // 15) + 1), 25)
        if SHAPE == "spike":                      # 10 -> 100 -> 10
            if t < 15:
                return (10, 10)
            if t < 35:
                return (100, 100)
            return (10, 100) if t < 50 else None
        return None

class FerreteriaUser(HttpUser):
    wait_time = between(0.5, 1.5)
    def auth(self):
        return {"Authorization": f"Bearer {USER_TOKEN}"}
    def internal(self):
        return {"X-Internal-Token": INTERNAL_TOKEN}

#PROVEEDORES
    #prueba de carga, estres y pico en get proveedores
    @tag("sup_list")
    @task
    def suppliers_list(self):
        self.client.get("/api/proveedores", headers=self.auth(), name="GET proveedores")
    #prueba de carga en post proveedores(escritura)
    @tag("sup_create")
    @task
    def supplier_create(self):
        unique = uuid.uuid4().int
        body = {
            "nit": str(unique)[:9],                      # único en cada petición
            "person_type": "JURIDICA",
            "legal_name": f"Proveedor Carga {str(unique)[:6]} S.A.S.",
            "trade_name": f"Carga {str(unique)[:6]}",
            "phone": "6068801234",
            "email": f"carga{str(unique)[:6]}@prueba.co",
            "address": "Cra. 23 # 65-10",
            "city": "Manizales",
            "delivery_days": 5,
        }
        self.client.post("/api/proveedores", json=body, headers=self.auth(), name="POST proveedores")

#catalogo
    #Prueba de carga, estres y pico en get catalogo
    @tag("cat_list")
    @task
    def products_list(self):
        self.client.get("/api/catalogo/products", headers=self.auth(), name="GET catalogo/products")
    #Carga en catalogo
    @tag("cat_detail")
    @task
    def product_detail(self):
        self.client.get("/api/catalogo/products/1", headers=self.auth(), name="GET catalogo/products/1")
    #Carga sin gateway
    @tag("cat_direct")
    @task
    def products_direct(self):
        self.client.get(f"{CATALOGO_DIRECT}/products", headers=self.internal(),
                        name="GET catalogo/products (directo)")

#Reportes
    #Carga y estres en get reportes
    @tag("rep_dashboard")
    @task
    def dashboard(self):
        self.client.get("/api/reportes/dashboard", headers=self.auth(), name="GET reportes/dashboard")
    #Carga y pico en get reportes stock
    @tag("rep_stock")
    @task
    def stock(self):
        self.client.get("/api/reportes/stock", headers=self.auth(), name="GET reportes/stock")

#Notificaciones
    #Carga y pico
    @tag("not_alert")
    @task
    def alert(self):
        body = {"product_id": 1, "product_code": "ELE-CAB-12", "product_name": "Cable calibre 12",
                "warehouse_id": 1, "current_quantity": 8, "minimum_stock": 50}
        self.client.post(f"{NOTIFICACIONES_DIRECT}/alerts", json=body, headers=self.internal(),
                         name="POST notificaciones/alerts (directo)")