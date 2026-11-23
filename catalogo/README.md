# Microservicio de Catálogo

Administra los productos que vende la ferretería, organizados en categorías y subcategorías.

## Tecnología

| | |
|---|---|
| Lenguaje | JavaScript (Node.js 22) |
| Framework | Express 4 |
| Base de datos | `catalogo_db` (MySQL 8) |
| Puerto del contenedor | 3000 (3001 en el computador) |
| Nombre en la red de Docker | `catalogo` (`http://catalogo:3000`) |

## Funcionalidades

- Registro, consulta y actualización de productos, con su código, unidad de medida, precio de venta, categoría y proveedor.
- Búsqueda y filtrado de productos por nombre, código, categoría o proveedor.
- Baja de productos sin borrarlos, para conservar su historial.
- Gestión de categorías y subcategorías.
- Al crear o actualizar un producto, valida con Proveedores que el proveedor exista y esté activo.

## Rutas

El Gateway quita el prefijo: el cliente llama `GET /api/catalogo/products/5` y este servicio recibe `GET /products/5`.

| Método y ruta | Qué hace | Roles | Respuestas |
|---|---|---|---|
| `GET /health` | Estado del servicio (no pide token) | — | 200 |
| `GET /products?search=&category_id=&supplier_id=&is_active=` | Busca y filtra productos | Los tres | 200 |
| `GET /products/{id}` | Consulta un producto | Los tres | 200, 404 |
| `POST /products` | Crea un producto | ADMINISTRADOR | 201, 400, 409, 503 |
| `PUT /products/{id}` | Actualiza un producto | ADMINISTRADOR | 200, 400, 404, 409, 503 |
| `PATCH /products/{id}/deactivate` | Da de baja un producto | ADMINISTRADOR | 200, 404 |
| `GET /categories?parent_category_id=` | Lista categorías y subcategorías | Los tres | 200 |
| `POST /categories` | Crea una categoría | ADMINISTRADOR | 201, 400, 409 |
| `PUT /categories/{id}` | Actualiza una categoría | ADMINISTRADOR | 200, 400, 404, 409 |
| `DELETE /categories/{id}` | Elimina una categoría | ADMINISTRADOR | 204, 404, 409 |

Los campos van en inglés y en `snake_case`: `code`, `name`, `description`, `category_id`, `supplier_id`, `unit_of_measure` (`UNIDAD`, `PAR`, `CAJA`, `METRO`, `ROLLO`, `KILOGRAMO`, `BULTO`, `LITRO` o `GALON`), `sale_price` e `is_active`.

Los errores tienen el formato `{"error", "message", "correlation_id"}`. Códigos usados: `DATOS_INVALIDOS`, `TOKEN_INTERNO_INVALIDO`, `NO_ENCONTRADO`, `DUPLICADO`, `CATEGORIA_EN_USO`, `SERVICIO_NO_DISPONIBLE`, `ERROR_INTERNO`.

## Variables de entorno

`DB_HOST`, `DB_PORT`, `DB_DATABASE`, `DB_USERNAME`, `DB_PASSWORD`, `INTERNAL_TOKEN` y `PROVEEDORES_URL`. Ver `.env.example`. Los valores reales viven en el `.env` de la raíz y nunca se suben a GitHub.

Las tablas se crean con `database/init.sql` la primera vez que arranca la base de datos.

## Cómo probarlo

Desde la raíz del repositorio:

    docker compose up -d --build catalogo
    docker logs -f catalogo

Directo al servicio (Thunder Client), con los headers `X-Internal-Token`, `X-User-Id`, `X-User-Role` y `X-Correlation-Id`:

    GET http://localhost:3001/health
    GET http://localhost:3001/products

A través del Gateway, con el token de Sanctum:

    GET http://localhost:8000/api/catalogo/products

## Se comunica con

- **Proveedores:** valida que el proveedor del producto exista y esté activo (tiempo máximo de espera: 2 segundos).
- Lo llaman **Inventario** y **Compras**, para validar productos, y **Reportes**, para consultar precios y categorías.

## Requisitos que cubre

REQ-F-005 y REQ-F-006.

## Documentación

- Contrato de API: [`docs/Entrega_2/contratos_api/catalogo.YAML`](../docs/Entrega_2/contratos_api/catalogo.YAML)
- Modelo de datos: [`docs/Entrega_2/codigos_dbml/catalogo_db.dbml`](../docs/Entrega_2/codigos_dbml/catalogo_db.dbml)