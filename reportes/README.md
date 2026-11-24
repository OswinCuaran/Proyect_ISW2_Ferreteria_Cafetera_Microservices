# Microservicio de Reportes y dashboard

Genera los reportes y los indicadores del inventario. No tiene base de datos: calcula todo en el momento con los productos de Catálogo y los saldos y ventas de Inventario.

## Tecnología

| | |
|---|---|
| Lenguaje | Python |
| Framework | Flask |
| Base de datos | No tiene |
| Puerto del contenedor | 5000 |
| Nombre del contenedor | `reportes` (`http://reportes:5000`, en tu equipo `http://localhost:5002`) |

## Funcionalidades

- Existencias por producto y bodega.
- Valor del inventario por bodega y por producto.
- Productos de mayor y menor rotación en un periodo.
- Sugerencias de cuándo y cuánto reabastecer, según las ventas y la temporada. Solo se muestran, no crean órdenes de compra.
- Dashboard con el valor total del inventario, los productos agotados, los productos bajo el mínimo y la rotación promedio.

## Se comunica con

- **Catálogo:** obtiene los productos activos con su nombre, categoría y precio de venta.
- **Inventario:** consulta el saldo de cada producto en cada bodega y las ventas registradas en el kardex.
- Lo llama el **Gateway**, solo para el Administrador.

## Rutas

Todas exigen el header `X-Internal-Token`, salvo `/health`. A través del Gateway van con el prefijo `/api/reportes`.

| Método | Ruta | Qué hace |
|---|---|---|
| GET | `/health` | Estado del servicio |
| GET | `/stock?warehouse_id=&category_id=` | Existencias por producto y bodega |
| GET | `/valuation?warehouse_id=` | Valor del inventario |
| GET | `/rotation?from=&to=&warehouse_id=&limit=` | Productos de mayor y menor rotación |
| GET | `/suggestions?warehouse_id=` | Sugerencias de reabastecimiento |
| GET | `/dashboard` | Indicadores del inventario |

En `/rotation`, las fechas `from` y `to` son obligatorias y van en formato `AAAA-MM-DD`.

## Reglas de negocio

- El inventario se valora a precio de venta, porque Catálogo no guarda el precio de costo.
- La rotación es lo vendido en el periodo dividido entre el stock promedio. Solo cuentan las ventas de mostrador y mayoristas.
- La demanda diaria sale de las ventas de los últimos 30 días. Se sugiere pedir cuando el stock alcanza para 15 días o menos, la cantidad sugerida cubre 30 días y la fecha descuenta los 7 días que tarda el proveedor en entregar.
- Si un producto no tuvo ventas pero está por debajo del mínimo, se sugiere reponer hasta el doble del mínimo.
- Entre el 15 de noviembre y el 15 de enero la demanda se multiplica por 1.3, por la temporada de fin de año.
- Si Catálogo o Inventario no responden en 2 segundos, responde `503 SERVICIO_NO_DISPONIBLE`.

Los valores de 7, 15 y 30 días y el factor de temporada están al inicio de `reports.py`.

## Cómo levantarlo

```bash
docker compose up -d --build reportes
docker logs -f reportes
```

Para que los reportes muestren datos, primero hay que registrar productos en Catálogo y entradas y ventas en Inventario.

## Requisitos que cubre

REQ-F-016, REQ-F-017 y REQ-F-018.

## Documentación

- Contrato de API: [`docs/Entrega_2/contratos_api/reportes.YAML`](../docs/Entrega_2/contratos_api/reportes.YAML)
