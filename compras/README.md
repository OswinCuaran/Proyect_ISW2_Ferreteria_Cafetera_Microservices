# Microservicio de Compras y devoluciones

Gestiona las órdenes de compra a los proveedores, la recepción de la mercancía y las devoluciones de clientes y a proveedores. Cada vez que llega o sale mercancía, le pide a Inventario que registre el movimiento.

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

- **Proveedores:** revisa que el proveedor de la orden exista y esté activo.
- **Inventario:** revisa que la bodega de destino exista y registra las entradas por recepción, las entradas por devolución de cliente y las salidas por devolución a proveedor.

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
| POST | `/returns` | Devolución de cliente o a proveedor |

Una orden tiene `supplier_id`, `destination_warehouse_id`, `expected_date`, `notes` e `items`, y cada producto lleva `product_id`, `quantity_ordered` y `unit_price`. En una recepción cada producto lleva `product_id` y `quantity_received`.

## Reglas de negocio

- Solo se recibe mercancía de órdenes `ENVIADA` o `RECIBIDA_PARCIAL`, y nunca más de lo que falta por recibir.
- Cuando llega todo lo pedido, la orden pasa sola a `RECIBIDA`; si falta algo, queda en `RECIBIDA_PARCIAL`.
- Una orden `RECIBIDA` o `CANCELADA` ya no cambia de estado.
- En una devolución de cliente solo vuelven al stock los productos en buen estado; los defectuosos se registran pero no se reingresan.
- Antes de registrar una recepción o una devolución se revisa que Inventario esté disponible. Si Inventario rechaza un movimiento, Compras no guarda la operación.
- El Operador solo recibe y devuelve mercancía de su propia bodega.

## Cómo levantarlo

```bash
docker compose up -d --build compras
docker logs -f compras
```

Al arrancar, el contenedor crea las tablas que todavía no existen.

## Requisitos que cubre

REQ-F-012, REQ-F-013 y REQ-F-014.

## Documentación

- Contrato de API: [`docs/Entrega_2/contratos_api/compras.YAML`](../docs/Entrega_2/contratos_api/compras.YAML)
- Modelo de datos: [`docs/Entrega_2/codigos_dbml/compras_devoluciones_db.dbml`](../docs/Entrega_2/codigos_dbml/compras_devoluciones_db.dbml)
