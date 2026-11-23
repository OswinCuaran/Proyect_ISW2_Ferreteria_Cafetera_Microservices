# Microservicio de Proveedores

Administra los proveedores a los que la ferretería les compra, con sus datos de contacto y su tiempo de entrega.

## Tecnología

| | |
|---|---|
| Lenguaje | Python 3.12 |
| Framework | Django + Django REST Framework |
| Base de datos | `proveedores_db` (MySQL 8) |
| Puerto del contenedor | 8000 (8002 en el computador) |
| Nombre en Kubernetes | `proveedores` (`http://proveedores:8000`) |

## Funcionalidades

- Registro, consulta y actualización de proveedores. El NIT no se puede repetir.
- Baja de proveedores sin borrarlos, para conservar su historial.
- Gestión de las personas de contacto de cada proveedor. Solo uno es el contacto principal.

## Rutas

El Gateway quita el prefijo: el cliente llama `GET /api/proveedores/5` y este servicio recibe `GET /5`. Solo el ADMINISTRADOR tiene permiso desde el Gateway.

| Método y ruta | Qué hace | Respuestas |
|---|---|---|
| `GET /health` | Estado del servicio (no pide token) | 200 |
| `GET /?search=&is_active=` | Lista y busca por NIT o razón social | 200, 400 |
| `POST /` | Registra un proveedor | 201, 400, 409 |
| `GET /{id}` | Consulta un proveedor | 200, 404 |
| `PUT /{id}` | Actualiza un proveedor | 200, 400, 404, 409 |
| `PATCH /{id}/deactivate` | Da de baja un proveedor | 200, 404 |
| `GET /{id}/contacts` | Lista los contactos | 200, 404 |
| `POST /{id}/contacts` | Agrega un contacto | 201, 400, 404 |

Los campos del JSON van en inglés y en `snake_case`: `nit`, `person_type` (`NATURAL` o `JURIDICA`), `legal_name`, `trade_name`, `phone`, `email`, `address`, `city`, `delivery_days`, `is_active`. Los contactos usan `name`, `position`, `phone`, `email` e `is_primary`.

Los errores tienen el formato `{"error", "message", "correlation_id"}`. Códigos usados: `DATOS_INVALIDOS`, `TOKEN_INTERNO_INVALIDO`, `NO_ENCONTRADO`, `DUPLICADO`, `ERROR_INTERNO`.

## Variables de entorno

`DB_HOST`, `DB_PORT`, `DB_DATABASE`, `DB_USERNAME`, `DB_PASSWORD` e `INTERNAL_TOKEN`. Ver `.env.example`. Los valores reales viven en el `.env` de la raíz y nunca se suben a GitHub.

## Cómo probarlo

Desde la raíz del repositorio:

    docker compose up -d --build proveedores
    docker logs -f proveedores

Directo al servicio (Thunder Client), con los headers `X-Internal-Token`, `X-User-Id`, `X-User-Role` y `X-Correlation-Id`:

    GET http://localhost:8002/health
    GET http://localhost:8002/

A través del Gateway, con el token de Sanctum de un Administrador:

    GET http://localhost:8000/api/proveedores

## Se comunica con

No llama a otros servicios. Lo llaman **Catálogo** y **Compras** para validar que un proveedor exista y esté activo.

## Requisitos que cubre

REQ-F-004.

## Documentación

- Contrato de API: [`docs/Entrega_2/contratos_api/proveedores.YAML`](../docs/Entrega_2/contratos_api/proveedores.YAML)
- Modelo de datos: [`docs/Entrega_2/codigos_dbml/proveedores_db.dbml`](../docs/Entrega_2/codigos_dbml/proveedores_db.dbml)