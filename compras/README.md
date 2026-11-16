# Microservicio de Compras y devoluciones

Gestiona las órdenes de compra a los proveedores, la recepción de la mercancía y las devoluciones de clientes y a proveedores.

## Tecnología

| | |
|---|---|
| Lenguaje | Python |
| Framework | Flask |
| Base de datos | `compras_db` (MySQL) |
| Puerto del contenedor | 5000 |
| Nombre en Kubernetes | `compras` (`http://compras:5000`) |

## Funcionalidades

- Creación y consulta de órdenes de compra, con sus productos, cantidades, precios y bodega de destino.
- Cambio de estado de las órdenes: borrador, enviada, recibida parcial, recibida o cancelada.
- Recepción total o parcial de la mercancía, que registra las entradas en Inventario.
- Devoluciones de clientes, que solo reingresan productos en buen estado, y devoluciones a proveedores, que descuentan el stock.

## Se comunica con

- **Proveedores:** valida el proveedor de la orden.
- **Catálogo:** valida los productos de la orden.
- **Inventario:** registra las entradas por recepción y por devolución.

## Requisitos que cubre

REQ-F-012, REQ-F-013 y REQ-F-014.

## Documentación

- Contrato de API: [`docs/Entrega_2/contratos_api/compras.YAML`](../docs/Entrega_2/contratos_api/compras.YAML)
- Modelo de datos: [`docs/Entrega_2/codigos_dbml/compras_devoluciones_db.dbml`](../docs/Entrega_2/codigos_dbml/compras_devoluciones_db.dbml)
