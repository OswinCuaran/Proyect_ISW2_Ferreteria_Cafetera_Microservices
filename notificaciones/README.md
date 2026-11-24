# Microservicio de Notificaciones y alertas

Envía por correo las alertas de stock bajo. No tiene base de datos: recibe la alerta de Inventario, busca a quién avisar y envía el correo.

## Tecnología

| | |
|---|---|
| Lenguaje | JavaScript (Node.js) |
| Framework | Express |
| Base de datos | No tiene |
| Puerto del contenedor | 3000 |
| Nombre del contenedor | `notificaciones` (`http://notificaciones:3000`, en tu equipo `http://localhost:3002`) |

## Funcionalidades

- Recibe de Inventario la alerta de un producto que quedó por debajo del stock mínimo.
- Busca en el Gateway a los Operadores de esa bodega y a los Administradores.
- Envía el correo con el producto, la bodega, la cantidad actual y el stock mínimo.
- Si no hay un servidor de correo configurado, escribe el correo en el log del contenedor, lo que permite probar las alertas sin una cuenta de correo.

## Se comunica con

- **Gateway:** consulta los usuarios activos de la bodega afectada y los Administradores.
- **Servidor de correo (SMTP):** envía la alerta.
- Lo llama **Inventario** cuando un producto baja del stock mínimo.

## Rutas

Todas exigen el header `X-Internal-Token`, salvo `/health`. Este servicio no pasa por el Gateway porque ningún usuario lo llama directamente.

| Método | Ruta | Qué hace |
|---|---|---|
| GET | `/health` | Estado del servicio |
| POST | `/alerts` | Recibe una alerta de stock bajo |

La alerta lleva `product_id`, `warehouse_id`, `current_quantity` y `minimum_stock`. Inventario también envía `product_code`, `product_name` y `warehouse` para que el correo muestre el nombre del producto y de la bodega.

## Reglas de negocio

- Responde `202` apenas recibe la alerta y envía el correo en segundo plano, para que Inventario no tenga que esperar.
- Si la consulta al Gateway o el envío del correo fallan, lo intenta hasta tres veces y deja el error en el log con el Correlation ID.
- Cada correo se envía una sola vez por persona, aunque un usuario aparezca en las dos consultas.
- Si `SMTP_HOST` está vacío, el correo aparece en el log como `[CORREO SIMULADO]`.

## Cómo levantarlo

```bash
docker compose up -d --build notificaciones
docker logs -f notificaciones
```

Las alertas se ven en el log del contenedor cuando una venta deja un producto por debajo de su stock mínimo.

## Requisitos que cubre

REQ-F-015.

## Documentación

- Contrato de API: [`docs/Entrega_2/contratos_api/notificaciones.YAML`](../docs/Entrega_2/contratos_api/notificaciones.YAML)
