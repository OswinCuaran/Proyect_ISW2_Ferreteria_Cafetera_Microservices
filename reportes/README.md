# Microservicio de Reportes y dashboard

Genera los reportes y los indicadores del inventario. Es un servicio sin estado: no tiene base de datos y calcula todo en el momento con los datos que consulta a otros servicios.

## Tecnología

| | |
|---|---|
| Lenguaje | Python 3.12 |
| Framework | Flask |
| Base de datos | Ninguna, es un servicio sin estado |
| Puerto del contenedor | 5000 (5002 en el computador) |
| Dirección interna | `http://reportes:5000` |

## Funcionalidades

- Reporte de existencias por producto y bodega.
- Valorización del inventario, por bodega y por producto.
- Productos de mayor y menor rotación en un periodo.
- Sugerencias de cuándo y cuánto reabastecer, según la rotación y la temporada. Solo se muestran, no crean órdenes.
- Dashboard con el valor total del inventario, los quiebres de stock, los productos bajo el mínimo y la rotación promedio.

Todas las rutas son solo para el rol ADMINISTRADOR; el Gateway revisa el rol.

## Rutas

| Método | Ruta | Parámetros | Descripción |
|---|---|---|---|
| GET | `/health` | | Estado del servicio (sin token) |
| GET | `/stock` | `warehouse_id`, `category_id` (opcionales) | Existencias por producto y bodega |
| GET | `/valuation` | `warehouse_id` (opcional) | Valor del inventario |
| GET | `/rotation` | `from`, `to` (obligatorios, `AAAA-MM-DD`), `warehouse_id`, `limit` (opcionales) | Mayor y menor rotación |
| GET | `/suggestions` | `warehouse_id` (opcional) | Sugerencias de reabastecimiento |
| GET | `/dashboard` | | Indicadores del inventario |

Los errores tienen la forma `{ "error", "message", "correlation_id" }`: `400 DATOS_INVALIDOS`, `401 TOKEN_INTERNO_INVALIDO`, `503 SERVICIO_NO_DISPONIBLE` cuando Catálogo o Inventario no responden en 2 segundos.

## Cómo se calcula

- **Existencias:** se piden los productos activos a Catálogo y, para cada uno, su stock a Inventario (varias consultas en paralelo).
- **Valorización:** cantidad × precio de venta (`sale_price`) del producto. El Catálogo no guarda precio de costo, por lo que el valor es **a precio de venta**.
- **Rotación:** unidades vendidas en el periodo ÷ stock promedio. El stock promedio se aproxima como stock actual + la mitad de lo vendido, por lo que el periodo debe ser cercano a la fecha actual. Solo cuentan las salidas de tipo venta (`SALIDA_VENTA_*`).
- **Sugerencias:** la demanda diaria sale de las ventas de los últimos 30 días. Se sugiere pedir cuando el stock dura 15 días o menos. La cantidad sugerida cubre 30 días, y la fecha sugerida descuenta 7 días de entrega del proveedor. Si no hubo ventas pero el saldo está bajo el mínimo, se sugiere reponer hasta el doble del mínimo.
- **Temporada:** del 15 de noviembre al 15 de enero ("Fin de año") la demanda se multiplica por 1.3.
- **Dashboard:** quiebre = producto con stock total 0. Bajo el mínimo = producto con mínimo configurado y cantidad menor a ese mínimo en alguna bodega.

Los valores de 7, 15, 30 y 1.3 son constantes al inicio de `reports.py`.

## Se comunica con

- **Inventario:** `GET /stock/{product_id}` (saldos) y `GET /movements?product_id=` (ventas).
- **Catálogo:** `GET /products` (nombre, categoría y precio).
- Lo consulta el **Gateway**, que valida el token y el rol.

## Variables de entorno

Los nombres están en `.env.example`. Los valores reales nunca se suben a GitHub.

| Variable | Para qué sirve |
|---|---|
| `INTERNAL_TOKEN` | Token compartido entre los servicios |
| `INVENTARIO_URL` | `http://inventario:8000` |
| `CATALOGO_URL` | `http://catalogo:3000` |
| `COMPRAS_URL` | `http://compras:5000` |

## Cómo probarlo

Desde la raíz del proyecto, con `TOKEN` igual al `INTERNAL_TOKEN` del `.env`:

```bash
docker compose up -d --build reportes
curl -s -H "X-Internal-Token: $TOKEN" http://localhost:5002/stock
curl -s -H "X-Internal-Token: $TOKEN" http://localhost:5002/valuation
curl -s -H "X-Internal-Token: $TOKEN" "http://localhost:5002/rotation?from=2026-11-01&to=2026-11-30"
curl -s -H "X-Internal-Token: $TOKEN" http://localhost:5002/suggestions
curl -s -H "X-Internal-Token: $TOKEN" http://localhost:5002/dashboard
```

Para que los reportes muestren datos hay que registrar entradas y ventas en Inventario.

## Requisitos que cubre

REQ-F-016, REQ-F-017 y REQ-F-018.

## Documentación

- Contrato de API: [`docs/Entrega_2/contratos_api/reportes.YAML`](../docs/Entrega_2/contratos_api/reportes.YAML)