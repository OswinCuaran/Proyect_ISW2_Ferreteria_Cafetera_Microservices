# Microservicio de Proveedores

Administra los proveedores a los que la ferretería les compra, con sus personas de contacto y su tiempo de entrega.

## Tecnología

| | |
|---|---|
| Lenguaje | Python |
| Framework | Django + Django REST Framework |
| Base de datos | `proveedores_db` (MySQL) |
| Puerto del contenedor | 8000 |
| Nombre del contenedor | `proveedores` (`http://proveedores:8000`, en tu equipo `http://localhost:8002`) |

## Funcionalidades

- Registro, consulta y actualización de proveedores, con búsqueda por NIT o razón social.
- Baja de proveedores sin borrarlos, para conservar su historial.
- Personas de contacto de cada proveedor, con un solo contacto principal.

## Se comunica con

No llama a otros servicios. Lo llama **Compras** para validar que el proveedor de una orden exista y esté activo.

## Rutas

Todas exigen el header `X-Internal-Token`, salvo `/health`. A través del Gateway van con el prefijo `/api/proveedores` y solo las puede usar el Administrador.

| Método | Ruta | Qué hace |
|---|---|---|
| GET | `/health` | Estado del servicio |
| GET | `/?search=&is_active=` | Lista los proveedores y busca por NIT o razón social |
| POST | `/` | Registra un proveedor |
| GET | `/{id}` | Consulta un proveedor |
| PUT | `/{id}` | Actualiza un proveedor |
| PATCH | `/{id}/deactivate` | Da de baja un proveedor |
| GET | `/{id}/contacts` | Lista los contactos de un proveedor |
| POST | `/{id}/contacts` | Agrega un contacto |

Campos del proveedor: `nit`, `person_type` (`NATURAL` o `JURIDICA`), `legal_name`, `trade_name`, `phone`, `email`, `address`, `city` y `delivery_days`. Campos del contacto: `name`, `position`, `phone`, `email` e `is_primary`.

## Reglas de negocio

- El NIT no se puede repetir: responde `409 DUPLICADO`.
- Un proveedor dado de baja no se borra, y Compras no le puede crear órdenes nuevas.
- Solo hay un contacto principal: al marcar uno, los demás dejan de serlo.
- El tiempo de entrega (`delivery_days`) es mínimo 1 día.

## Cómo levantarlo

```bash
docker compose up -d --build proveedores
docker logs -f proveedores
```

Al arrancar, el contenedor crea las tablas con las migraciones de Django.

## Requisitos que cubre

REQ-F-004.

## Documentación

- Contrato de API: [`docs/Entrega_2/contratos_api/proveedores.YAML`](../docs/Entrega_2/contratos_api/proveedores.YAML)
- Modelo de datos: [`docs/Entrega_2/codigos_dbml/proveedores_db.dbml`](../docs/Entrega_2/codigos_dbml/proveedores_db.dbml)
