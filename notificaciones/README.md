# Microservicio de Notificaciones y alertas

Envía por correo las alertas de stock bajo. Es un servicio sin estado: no tiene base de datos y no guarda información.

## Tecnología

| | |
|---|---|
| Lenguaje | JavaScript (Node.js 22) |
| Framework | Express |
| Base de datos | Ninguna, es un servicio sin estado |
| Puerto del contenedor | 3000 (3002 en el computador) |
| Dirección interna | `http://notificaciones:3000` |

## Funcionalidades

- Recibe de Inventario la alerta de un producto que quedó por debajo del stock mínimo.
- Valida los datos y responde `202` de inmediato.
- En segundo plano consulta al Gateway los destinatarios (los Operadores de la bodega afectada y los Administradores) y les envía el correo.
- Si falla la consulta o el envío, reintenta hasta 3 veces y deja el error en el log con el Correlation ID de la petición.
- Si no hay un servidor SMTP configurado, escribe el correo en el log (`[CORREO SIMULADO]`), lo que permite probar sin una cuenta de correo.

No se expone a través del Gateway: solo recibe llamadas internas, con el token interno.

## Rutas

| Método | Ruta | Descripción | Token |
|---|---|---|---|
| GET | `/health` | Estado del servicio | No |
| POST | `/alerts` | Recibe una alerta de stock bajo | Sí |

### `POST /alerts`

Cuerpo:

```json
{
  "product_id": 1,
  "product_code": "ELE-CAB-12",
  "product_name": "Cable electrico calibre 12 AWG",
  "warehouse_id": 1,
  "current_quantity": 8,
  "minimum_stock": 50
}
```

| Código | Cuándo |
|---|---|
| 202 | Alerta recibida. El correo se envía en segundo plano. |
| 400 | `DATOS_INVALIDOS`: falta un campo o tiene un tipo incorrecto. |
| 401 | `TOKEN_INTERNO_INVALIDO`: falta el token o es incorrecto. |

Los errores tienen la forma `{ "error", "message", "correlation_id" }`.

## Se comunica con

- **Gateway:** `GET /api/internal/users?warehouse_id=<bodega>&role=OPERADOR` y `GET /api/internal/users?role=ADMINISTRADOR`, con el token interno y 2 segundos de espera máxima. El Administrador no tiene bodega, por eso se consulta sin `warehouse_id`.
- **Servidor SMTP:** envía el correo de alerta.
- Lo llama **Inventario**.

## Variables de entorno

Los nombres están en `.env.example`. Los valores reales nunca se suben a GitHub.

| Variable | Para qué sirve |
|---|---|
| `INTERNAL_TOKEN` | Token compartido entre los servicios |
| `GATEWAY_URL` | Dirección del Gateway (`http://gateway:8000`) |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM` | Servidor de correo. Si `SMTP_HOST` está vacío, el correo se simula en el log |

## Cómo probarlo

Desde la raíz del proyecto:

```bash
docker compose up -d --build notificaciones
curl -i http://localhost:3002/health

curl -i -X POST http://localhost:3002/alerts \
  -H "X-Internal-Token: $TOKEN" -H "Content-Type: application/json" \
  -d '{"product_id":1,"product_code":"TOR-001","product_name":"Tornillo","warehouse_id":1,"current_quantity":8,"minimum_stock":50}'

docker compose logs --tail=15 notificaciones
```

## Requisitos que cubre

REQ-F-015.

## Documentación

- Contrato de API: [`docs/Entrega_2/contratos_api/notificaciones.YAML`](../docs/Entrega_2/contratos_api/notificaciones.YAML)