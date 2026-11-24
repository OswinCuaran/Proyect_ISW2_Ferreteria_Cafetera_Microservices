# API Gateway

Es la única entrada al sistema. Recibe todas las peticiones de los usuarios, revisa quién es y qué puede hacer según su rol, y las envía al microservicio que corresponde. También administra los usuarios, los roles y el inicio de sesión.

## Tecnología

| | |
|---|---|
| Lenguaje | PHP 8.4 |
| Framework | Laravel con Sanctum |
| Base de datos | `gateway_db` (MySQL) |
| Puerto del contenedor | 8000 |
| Nombre del contenedor | `gateway` (`http://gateway:8000`, en tu equipo `http://localhost:8000`) |

## Funcionalidades

- Inicio y cierre de sesión con tokens de Sanctum.
- Recuperación de la contraseña con la pregunta de seguridad y cambio de contraseña.
- Registro y administración de usuarios con su rol, su bodega y su pregunta de seguridad.
- Permisos por rol para cada ruta de cada microservicio: Administrador, Operador y Vendedor.
- Redirección de `/api/{servicio}/...` al microservicio que corresponde, con el token interno y los datos del usuario en los headers.
- Correlation ID en cada petición para poder seguirla en los logs de todos los servicios.

## Se comunica con

- Envía las peticiones de los usuarios a **Inventario**, **Proveedores**, **Catálogo**, **Compras** y **Reportes**.
- Lo llama **Notificaciones** para saber a qué usuarios avisar de una alerta.

## Rutas

Las tres primeras son públicas y permiten 10 intentos por minuto. Las demás piden el token de Sanctum en el header `Authorization: Bearer`. El registro, los usuarios, los roles y las preguntas de seguridad son solo para el Administrador.

| Método | Ruta | Qué hace |
|---|---|---|
| POST | `/api/login` | Inicia sesión y devuelve el token |
| GET | `/api/password/question?email=` | Muestra la pregunta de seguridad del usuario |
| POST | `/api/password/recover` | Cambia la contraseña con la respuesta de seguridad |
| POST | `/api/logout` | Cierra la sesión |
| GET | `/api/me` | Datos del usuario que inició sesión |
| PUT | `/api/password` | Cambia la contraseña |
| POST | `/api/register` | Registra un usuario |
| GET | `/api/users?role=&warehouse_id=&is_active=` | Lista los usuarios |
| PUT | `/api/users/{id}` | Actualiza un usuario |
| PATCH | `/api/users/{id}/deactivate` | Desactiva un usuario |
| PATCH | `/api/users/{id}/activate` | Vuelve a activar un usuario |
| GET | `/api/roles` | Lista los roles con sus permisos |
| GET | `/api/security-questions` | Lista las preguntas de seguridad |
| Todos | `/api/{servicio}/{ruta}` | Envía la petición a `inventario`, `proveedores`, `catalogo`, `compras` o `reportes` |
| GET | `/api/internal/users?role=&warehouse_id=` | Usuarios para Notificaciones, con el header `X-Internal-Token` |

Un usuario tiene `document_type` (`CC`, `CE` o `PA`), `document_number`, `first_name`, `last_name`, `email`, `password`, `role_id`, `warehouse_id`, `security_question_id` y `security_answer`.

## Reglas de negocio

- Cada ruta de un microservicio exige un permiso definido en `config/permissions.php`. Si la ruta no está en la lista o el rol no tiene el permiso, responde `403 SIN_PERMISO`.
- El Operador y el Vendedor deben tener una bodega asignada. El Administrador no tiene bodega porque trabaja con las tres.
- El correo y el documento no se pueden repetir: responde `409 CORREO_DUPLICADO` o `409 DOCUMENTO_DUPLICADO`.
- Un usuario desactivado no puede iniciar sesión, y el Administrador no puede desactivarse ni cambiarse el rol a sí mismo.
- La contraseña y la respuesta de seguridad se guardan con hash, nunca como texto.
- El token interno nunca llega al usuario: el Gateway lo agrega a cada petición junto con `X-User-Id`, `X-User-Role`, `X-User-Warehouse` y `X-Correlation-Id`.
- Si un microservicio no responde en 2 segundos, responde `503 SERVICIO_NO_DISPONIBLE`.

## Cómo levantarlo

```bash
cp gateway/.env.example gateway/.env
docker compose up -d --build gateway
docker logs -f gateway
```

En `gateway/.env` se completan la contraseña de la base de datos, el token interno y los datos del primer Administrador (`ADMIN_EMAIL`, `ADMIN_PASSWORD` y `ADMIN_SECURITY_ANSWER`). El token interno tiene que coincidir con el del `.env` de la raíz, porque con él los microservicios reconocen que la petición viene del Gateway.

Al arrancar, el contenedor genera la llave de la aplicación si no existe, crea las tablas y carga los roles, los permisos, las preguntas de seguridad y el primer Administrador. Si el Administrador ya existe, lo deja como está.

## Requisitos que cubre

REQ-F-001, REQ-F-002, REQ-F-003, REQ-NF-002 y REQ-NF-006.

## Documentación

- Contrato de API: [`docs/Entrega_2/contratos_api/gateway.YAML`](../docs/Entrega_2/contratos_api/gateway.YAML)
- Modelo de datos: [`docs/Entrega_2/codigos_dbml/gateway_db.dbml`](../docs/Entrega_2/codigos_dbml/gateway_db.dbml)
