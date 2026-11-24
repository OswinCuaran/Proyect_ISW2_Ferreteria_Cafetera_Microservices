# Pruebas de rendimiento

Pruebas de carga del sistema hechas con Locust. Todas las peticiones entran por el API Gateway, igual que las de un usuario real, y llegan a los microservicios con el token interno.

Locust no es un microservicio ni corre en un contenedor. Es un programa de Python que se ejecuta desde la terminal, simula muchos usuarios a la vez y mide el tiempo de respuesta, las peticiones por segundo y la tasa de error de cada endpoint.

## Archivos

| Archivo | Qué contiene |
|---|---|
| `locustfile_oswin.py` | Las quince pruebas de Oswin sobre el Gateway, Inventario y Compras |
| `requirements.txt` | Dependencias: Locust y python-dotenv |
| `.env.example` | Variables que necesitan las pruebas |
| `resultados/` | Reportes HTML de cada ejecución |

## Datos de prueba

Antes de empezar, las pruebas inician sesión como Administrador y dejan listo lo que necesitan. Si algo ya existe de una ejecución anterior, lo reutilizan:

- Un Operador y un Vendedor de la bodega de Manizales.
- Un proveedor, la categoría "Pruebas de carga" y cinco productos con código `LOC-`.
- Un saldo de un millón de unidades de cada producto en Manizales, para que las ventas y los traslados nunca se queden sin existencias.
- Una orden de compra enviada con cantidades grandes, sobre la que se registran las recepciones, y una orden en borrador para consultarla.

Cada rol inicia sesión una sola vez y todos sus usuarios simulados comparten el token. Así el límite de 10 inicios de sesión por minuto del Gateway no afecta las demás pruebas.

## Pruebas de Oswin

| # | Prueba | Rol | Ruta |
|---|---|---|---|
| O01 | Iniciar sesión | Administrador | `POST /api/login` |
| O02 | Consultar el usuario de la sesión | Vendedor | `GET /api/me` |
| O03 | Listar usuarios | Administrador | `GET /api/users` |
| O04 | Ruta sin permiso para el rol | Vendedor | `GET /api/compras/orders` |
| O05 | Listar bodegas | Operador | `GET /api/inventario/warehouses` |
| O06 | Consultar stock de un producto | Vendedor | `GET /api/inventario/stock/{id}` |
| O07 | Registrar una venta | Vendedor | `POST /api/inventario/movements/exits` |
| O08 | Registrar una entrada | Operador | `POST /api/inventario/movements/entries` |
| O09 | Consultar el kardex de un producto | Operador | `GET /api/inventario/movements` |
| O10 | Trasladar entre bodegas | Operador | `POST /api/inventario/transfers` |
| O11 | Productos bajo el stock mínimo | Operador | `GET /api/inventario/stock/below-minimum` |
| O12 | Listar órdenes enviadas | Administrador | `GET /api/compras/orders?status=ENVIADA` |
| O13 | Crear una orden de compra | Administrador | `POST /api/compras/orders` |
| O14 | Consultar una orden de compra | Operador | `GET /api/compras/orders/{id}` |
| O15 | Registrar la recepción de mercancía | Operador | `POST /api/compras/orders/{id}/receptions` |

En O01 una respuesta `429` también cuenta como correcta, porque muestra que el Gateway frena los intentos repetidos de inicio de sesión. En O04 lo correcto es `403`: mide qué tan rápido el Gateway rechaza una ruta que el rol no puede usar.

Los usuarios simulados se reparten entre los roles: por cada administrador hay dos operadores y tres vendedores. Cada usuario espera entre uno y tres segundos entre una petición y otra.

## Escenarios

| Escenario | Usuarios | Usuarios nuevos por segundo | Duración | Qué busca |
|---|---|---|---|---|
| Carga normal | 50 | 10 | 40 s | Un día normal de trabajo en las tres sedes. Es la carga del requisito REQ-NF-005. |
| Carga pico | 150 | 50 | 40 s | La temporada de fin de año, cuando muchos usuarios llegan casi al mismo tiempo. |
| Estrés | 300 | 20 | 40 s | Una carga mayor a la esperada, para ver dónde empiezan los errores o las respuestas lentas. |

## Cómo correrlas

Primero se levantan todos los contenedores desde la raíz del repositorio con `docker compose up -d --build`. Luego, dentro de `pruebas`, se crea el `.env` a partir de `.env.example` con el correo y la contraseña del Administrador del Gateway y una contraseña de al menos 8 caracteres para los usuarios de prueba.

En Ubuntu:

```bash
cd pruebas
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m locust -f locustfile_oswin.py --autostart -u 50 -r 10 -t 40s --html resultados/1_carga_normal.html
```

En Windows (PowerShell):

```powershell
cd pruebas
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m locust -f locustfile_oswin.py --autostart -u 50 -r 10 -t 40s --html resultados/1_carga_normal.html
```

La prueba arranca sola y se puede seguir en `http://localhost:8089`. En la pestaña Charts están las gráficas de peticiones por segundo, tiempos de respuesta y usuarios. A los 40 segundos se detiene y los resultados quedan en pantalla. Al cerrar Locust con `Ctrl + C`, el reporte HTML se guarda en `resultados/`.

Para los otros escenarios se cambian los usuarios, la velocidad y el nombre del reporte:

```bash
-u 150 -r 50 -t 40s --html resultados/2_carga_pico.html
-u 300 -r 20 -t 40s --html resultados/3_estres.html
```

## Resultados

Al terminar cada ejecución, la terminal muestra si se cumple el requisito REQ-NF-005: que el 95 % de las consultas de stock (O06) responda en menos de 2 segundos.

Los tiempos dependen del computador, porque Locust y los trece contenedores corren en la misma máquina. Si en el escenario de estrés aparecen errores `503 SERVICIO_NO_DISPONIBLE`, quiere decir que un microservicio tardó más de 2 segundos en responderle al Gateway.
