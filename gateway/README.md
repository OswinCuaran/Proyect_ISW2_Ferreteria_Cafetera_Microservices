# API Gateway

Único punto de entrada al sistema. Recibe todas las peticiones externas, autentica al usuario con Sanctum, revisa que su rol tenga permiso y redirige cada petición al microservicio que corresponde. También administra los usuarios del sistema.

## Tecnología

| | |
|---|---|
| Lenguaje | PHP 8.3 |
| Framework | Laravel con Sanctum |
| Base de datos | `gateway_db` (MySQL) |
| Puerto del contenedor | 8000 |
| Acceso externo | NodePort 30080 en Kubernetes |

## Funcionalidades

- Registro de usuarios con su rol, su bodega y su pregunta de seguridad (solo el Administrador).
- Inicio y cierre de sesión con tokens de Sanctum.
- Recuperación de la contraseña con la pregunta de seguridad y cambio de contraseña.
- Gestión de usuarios y roles: Administrador, Operador y Vendedor.
- Middleware de entrada: Correlation ID, límite de peticiones, validación del token y control de rol.
- Redirección de `/api/{servicio}/...` al microservicio correspondiente, agregando el token interno y los encabezados `X-User-Id` y `X-User-Rol`.
- Consulta interna de los usuarios de una bodega, que usa Notificaciones para saber a quién avisar.

## Se comunica con

Todos los microservicios: es el único que los llama desde afuera.

## Requisitos que cubre

REQ-F-001, REQ-F-002, REQ-F-003, REQ-NF-002 y REQ-NF-006.

## Documentación

- Contrato de API: [`docs/Entrega_2/contratos_api/gateway.YAML`](../docs/Entrega_2/contratos_api/gateway.YAML)
- Modelo de datos: [`docs/Entrega_2/codigos_dbml/gateway_db.dbml`](../docs/Entrega_2/codigos_dbml/gateway_db.dbml)
