# Microservicio de Inventario

Es el corazón del sistema. Lleva las existencias de cada producto en cada bodega, registra todo lo que entra y sale, y avisa cuando un producto queda por debajo de su stock mínimo.

## Tecnología

| | |
|---|---|
| Lenguaje | Python |
| Framework | Django |
| Base de datos | `inventario_db` (MySQL) |
| Puerto del contenedor | 8000 |
| Nombre del contenedor | `inventario` (`http://inventario:8000`, en tu equipo `http://localhost:8001`) |

## Funcionalidades

- Gestión de las bodegas de Manizales, Pereira y Armenia.
- Registro de entradas, ventas y ajustes. Las ventas descuentan el saldo de inmediato y se rechazan si no hay existencias suficientes.
- Traslados entre bodegas en una sola operación.
- Consulta de la disponibilidad de un producto en cada bodega y en las tres sedes.
- Kardex de cada producto: historial de movimientos que no se puede modificar ni borrar.
- Configuración del stock mínimo y lista de productos por debajo de él, que alimenta las alertas en pantalla.

## Se comunica con

- **Catálogo:** valida que el producto exista y esté activo.
- **Notificaciones:** le avisa cuando un producto baja del stock mínimo.
- Lo llaman **Compras**, para registrar entradas y devoluciones, y **Reportes**, para consultar saldos y movimientos.

## Rutas

Todas exigen el header `X-Internal-Token`, salvo `/health`. A través del Gateway van con el prefijo `/api/inventario`.

| Método | Ruta | Qué hace |
|---|---|---|
| GET | `/health` | Estado del servicio |
| GET | `/warehouses?is_active=true` | Lista las bodegas |
| POST | `/warehouses` | Crea una bodega |
| PUT | `/warehouses/{id}` | Actualiza una bodega |
| PATCH | `/warehouses/{id}/deactivate` | Desactiva una bodega sin existencias |
| PATCH | `/warehouses/{id}/activate` | Vuelve a activar una bodega |
| POST | `/movements/entries` | Entrada (`ENTRADA_COMPRA`, `DEVOLUCION_CLIENTE`) |
| POST | `/movements/exits` | Venta o salida (`SALIDA_VENTA_MOSTRADOR`, `SALIDA_VENTA_MAYORISTA`, `DEVOLUCION_PROVEEDOR`) |
| POST | `/movements/adjustments` | Ajuste (`AJUSTE_POSITIVO`, `AJUSTE_NEGATIVO`), con motivo obligatorio |
| GET | `/movements?product_id=&warehouse_id=&from=&to=` | Kardex de un producto |
| POST | `/transfers` | Traslado entre bodegas |
| GET | `/stock/{product_id}` | Disponibilidad en cada bodega y total |
| GET | `/stock/below-minimum?warehouse_id=` | Productos bajo el stock mínimo |
| PUT | `/stock/{warehouse_id}/{product_id}/minimum` | Configura el stock mínimo |

## Reglas de negocio

- Una venta o salida se rechaza con `409 EXISTENCIAS_INSUFICIENTES` si no hay saldo, y no descuenta nada.
- Dos ventas al mismo tiempo no pueden descontar del mismo saldo: la existencia se bloquea durante la transacción.
- La misma referencia de entrada no puede sumar dos veces al stock del mismo producto.
- El Operador y el Vendedor solo registran movimientos en su propia bodega (`X-User-Warehouse`).
- Si el saldo baja del stock mínimo, se avisa a Notificaciones una sola vez hasta que se recupere.
- Si Catálogo o Notificaciones no responden, el movimiento se registra igual y queda una advertencia en el log.
- Los movimientos (kardex) no se pueden modificar ni borrar.

## Cómo levantarlo

```bash
docker compose up -d --build inventario
docker logs -f inventario
```

Al arrancar, el contenedor crea las tablas y los datos iniciales (tipos de movimiento y las bodegas de Manizales, Pereira y Armenia).

## Requisitos que cubre

REQ-F-007, REQ-F-008, REQ-F-009, REQ-F-010, REQ-F-011 y REQ-F-015.

## Documentación

- Contrato de API: [`docs/Entrega_2/contratos_api/inventario.YAML`](../docs/Entrega_2/contratos_api/inventario.YAML)
- Modelo de datos: [`docs/Entrega_2/codigos_dbml/inventario_db.dbml`](../docs/Entrega_2/codigos_dbml/inventario_db.dbml)
