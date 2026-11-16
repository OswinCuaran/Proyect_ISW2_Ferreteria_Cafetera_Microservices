# Microservicio de Inventario

Es el corazón del sistema. Lleva las existencias de cada producto en cada bodega, registra todo lo que entra y sale, y avisa cuando un producto queda por debajo de su stock mínimo.

## Tecnología

| | |
|---|---|
| Lenguaje | Python |
| Framework | Django |
| Base de datos | `inventario_db` (MySQL) |
| Puerto del contenedor | 8000 |
| Nombre en Kubernetes | `inventario` (`http://inventario:8000`) |

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

## Requisitos que cubre

REQ-F-007, REQ-F-008, REQ-F-009, REQ-F-010, REQ-F-011 y REQ-F-015.

## Documentación

- Contrato de API: [`docs/Entrega_2/contratos_api/inventario.YAML`](../docs/Entrega_2/contratos_api/inventario.YAML)
- Modelo de datos: [`docs/Entrega_2/codigos_dbml/inventario_db.dbml`](../docs/Entrega_2/codigos_dbml/inventario_db.dbml)
