# Microservicio de Compras y devoluciones

Gestiona las órdenes de compra a los proveedores, la recepción de la mercancía y las devoluciones de clientes y a proveedores.

## Tecnología

| | |
|---|---|
| Lenguaje | Python |
| Framework | Flask |
| Base de datos | `compras_db` (MySQL) |
| Puerto del contenedor | 5000 |
| Nombre del contenedor | `compras` (`http://compras:5000`, en tu equipo `http://localhost:5001`) |

## Funcionalidades

- Creación y consulta de órdenes de compra, con sus productos, cantidades, precios y bodega de destino.
- Cambio de estado de las órdenes: borrador, enviada, recibida parcial, recibida o cancelada.
- Recepción total o parcial de la mercancía, que registra las entradas en Inventario.
- Devoluciones de clientes, que solo reingresan productos en buen estado, y devoluciones a proveedores, que descuentan el stock.

## Se comunica con

- **Proveedores:** valida el proveedor de la orden.
- **Catálogo:** valida los productos de la orden.
- **Inventario:** registra las entradas por recepción y por devolución.

## Estructura

Sigue la estructura del ejercicio de Flask visto en clase:

| Archivo | Qué hace |
|---|---|
| `database.py` | Arma la conexión a MySQL con las variables de entorno |
| `create_tables.py` | Crea las tablas si no existen al arrancar el contenedor |
| `app.py` | Crea la app, valida el token interno y responde los errores en el mismo formato |
| `orders.py` | Rutas de órdenes de compra y recepciones, con SQL en `text()` |
| `returns.py` | Rutas de devoluciones |
| `clients.py` | Llamadas a Inventario y Proveedores con el token interno |
| `utils.py` | Validaciones y formato de errores |

## Rutas

Todas exigen el header `X-Internal-Token`, salvo `/health`. A través del Gateway van con el prefijo `/api/compras`.

| Método | Ruta | Qué hace |
|---|---|---|
| GET | `/health` | Estado del servicio |
| GET | `/orders?status=&supplier_id=` | Lista las órdenes de compra |
| POST | `/orders` | Crea una orden en BORRADOR |
| GET | `/orders/{id}` | Orden con lo pedido, lo recibido, lo pendiente y sus recepciones |
| PATCH | `/orders/{id}/status` | Envía (`ENVIADA`) o cancela (`CANCELADA`) una orden |
| POST | `/orders/{id}/receptions` | Recepción total o parcial: cada producto entra al stock en Inventario |
| GET | `/returns?type=&warehouse_id=` | Lista las devoluciones |
| POST | `/returns` | Devolución de cliente (reingresa lo que está en buen estado) o a proveedor (descuenta del stock) |

## Reglas de negocio

- Solo se recibe mercancía de órdenes `ENVIADA` o `RECIBIDA_PARCIAL`, y nunca más de lo pendiente.
- Cuando llega todo lo pedido, la orden pasa sola a `RECIBIDA`; si falta algo, a `RECIBIDA_PARCIAL`.
- Una orden `RECIBIDA` o `CANCELADA` ya no cambia de estado.
- Si Inventario rechaza un movimiento (por ejemplo, sin existencias), la recepción o la devolución se deshace completa.
- El Operador solo recibe y devuelve mercancía de su propia bodega.

## Requisitos que cubre

REQ-F-012, REQ-F-013 y REQ-F-014.

## Documentación

- Contrato de API: [`docs/Entrega_2/contratos_api/compras.YAML`](../docs/Entrega_2/contratos_api/compras.YAML)
- Modelo de datos: [`docs/Entrega_2/codigos_dbml/compras_devoluciones_db.dbml`](../docs/Entrega_2/codigos_dbml/compras_devoluciones_db.dbml)
