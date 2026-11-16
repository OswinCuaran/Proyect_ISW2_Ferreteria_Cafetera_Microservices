# Microservicio de Reportes y dashboard

Genera los reportes y los indicadores del inventario. Es un servicio sin estado: no tiene base de datos y calcula todo en el momento con los datos que consulta a otros servicios.

## Tecnología

| | |
|---|---|
| Lenguaje | Python |
| Framework | Flask |
| Base de datos | Ninguna, es un servicio sin estado |
| Puerto del contenedor | 5000 |
| Nombre en Kubernetes | `reportes` (`http://reportes:5000`) |

## Funcionalidades

- Reporte de existencias por producto y bodega.
- Valorización del inventario.
- Productos de mayor y menor rotación en un periodo.
- Sugerencias de cuándo y cuánto reabastecer, según la rotación y la temporada. Solo se muestran, no crean órdenes.
- Dashboard con el valor total del inventario, los quiebres de stock, los productos bajo el mínimo y la rotación promedio.

## Se comunica con

- **Inventario:** consulta saldos y movimientos.
- **Catálogo:** consulta precios y categorías.

## Requisitos que cubre

REQ-F-016, REQ-F-017 y REQ-F-018.

## Documentación

- Contrato de API: [`docs/Entrega_2/contratos_api/reportes.YAML`](../docs/Entrega_2/contratos_api/reportes.YAML)
