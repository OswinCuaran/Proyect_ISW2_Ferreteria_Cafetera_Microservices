# Microservicio de Notificaciones y alertas

Envía por correo las alertas de stock bajo. Es un servicio sin estado: no tiene base de datos y no guarda información.

## Tecnología

| | |
|---|---|
| Lenguaje | JavaScript (Node.js) |
| Framework | Express |
| Base de datos | Ninguna, es un servicio sin estado |
| Puerto del contenedor | 3000 |
| Nombre en Kubernetes | `notificaciones` (`http://notificaciones:3000`) |

## Funcionalidades

- Recibe de Inventario la alerta de un producto que quedó por debajo del stock mínimo.
- Responde de inmediato y, en segundo plano, consulta los destinatarios y envía el correo.
- Si el envío falla, reintenta y deja el error en el log con el Correlation ID de la petición.

No se expone a través del Gateway: solo recibe llamadas internas del clúster, con el token interno.

## Se comunica con

- **Gateway:** consulta el administrador y los operadores de la bodega afectada.
- **Servidor SMTP:** envía el correo de alerta.
- Lo llama **Inventario**.

## Requisitos que cubre

REQ-F-015.

## Documentación

- Contrato de API: [`docs/Entrega_2/contratos_api/notificaciones.YAML`](../docs/Entrega_2/contratos_api/notificaciones.YAML)
