# Sistema de Gestión de Inventarios - Ferretería Cafetera

Proyecto de **Ingeniería de Software II** de la Universidad Nacional de Colombia, sede Manizales.

Sistema de gestión de inventarios basado en una arquitectura de microservicios para Ferretería Cafetera, una pyme distribuidora de materiales de construcción con sede principal en Manizales y bodegas en Pereira y Armenia. El sistema reemplaza el kardex manual de la empresa, descuenta el inventario en el momento de cada venta, permite consultar la disponibilidad en las tres sedes y genera alertas cuando un producto baja de su stock mínimo.

## Equipo

- Oswin Olsman Cuaran Cuaran
- Santiago Lopez

**Docente:** Albeiro Montes

## Arquitectura

![Arquitectura de microservicios](docs/Entrega_2/Arquitectura_y_Modelos_ER.jpg)

Todas las peticiones entran por un API Gateway propio, que valida el token de Sanctum y el rol del usuario y redirige cada petición al microservicio que corresponde. Los microservicios se comunican entre sí por medio de API REST y se ubican por el nombre de su contenedor dentro de la red de Docker Compose. Cada servicio administra únicamente su propia base de datos y solo atiende peticiones que traigan el token interno.

| Componente | Carpeta | Framework | Base de datos |
|---|---|---|---|
| API Gateway (usuarios y autenticación) | [`gateway/`](gateway/README.md) | Laravel + Sanctum | gateway_db |
| Inventario | [`inventario/`](inventario/README.md) | Django | inventario_db |
| Proveedores | [`proveedores/`](proveedores/README.md) | Django | proveedores_db |
| Catálogo | [`catalogo/`](catalogo/README.md) | Express | catalogo_db |
| Compras y devoluciones | [`compras/`](compras/README.md) | Flask | compras_db |
| Notificaciones y alertas | [`notificaciones/`](notificaciones/README.md) | Express | Sin base de datos |
| Reportes y dashboard | [`reportes/`](reportes/README.md) | Flask | Sin base de datos |

Cada carpeta tiene su propio README con las funcionalidades del servicio, su tecnología y los servicios con los que se comunica.

## Estructura del repositorio

```
├── gateway/          API Gateway en Laravel con Sanctum
├── inventario/       Microservicio de Inventario en Django
├── proveedores/      Microservicio de Proveedores en Django
├── catalogo/         Microservicio de Catálogo en Express
├── compras/          Microservicio de Compras y devoluciones en Flask
├── notificaciones/   Microservicio de Notificaciones y alertas en Express
├── reportes/         Microservicio de Reportes y dashboard en Flask
├── k8s/              Manifiestos de Kubernetes (próxima entrega)
├── pruebas/          Pruebas de rendimiento con Locust
├── docs/
│   ├── Entrega_1/    Investigación, requisitos y bitácora de IA
│   └── Entrega_2/    Arquitectura, modelos entidad relación, contratos de API, documento y bitácora
└── README.md
```

Las bases de datos no tienen carpeta propia: cada una corre en su propio contenedor de MySQL, que crea la base de datos automáticamente la primera vez que arranca.

## Cómo levantarlo

Se necesita Docker con Docker Compose. Desde la raíz del repositorio:

```bash
cp .env.example .env
cp gateway/.env.example gateway/.env
```

En los dos archivos se completan las contraseñas. El `INTERNAL_TOKEN` tiene que ser igual en ambos, porque con él los microservicios reconocen que la petición viene del Gateway. Luego:

```bash
docker compose up -d --build
docker compose ps
```

Cada servicio crea sus tablas al arrancar y el Gateway crea el primer Administrador con los datos `ADMIN_*` del `gateway/.env`. Todas las peticiones entran por `http://localhost:8000/api`; la primera es `POST /api/login` con ese Administrador.

| Servicio | Puerto en el computador | Base de datos |
|---|---|---|
| Gateway | 8000 | 3307 |
| Inventario | 8001 | 3308 |
| Proveedores | 8002 | 3309 |
| Catálogo | 3001 | 3310 |
| Compras | 5001 | 3311 |
| Notificaciones | 3002 | — |
| Reportes | 5002 | — |

Los microservicios también quedan publicados en el computador para hacer pruebas directas, pero sin el header `X-Internal-Token` responden 401.

Para correr un servicio fuera de Docker, se copia su `.env.example` como `.env` dentro de su carpeta. Ahí la base de datos se busca en `127.0.0.1` con el puerto de la tabla, y los demás servicios en `http://localhost` con su puerto.

## Cómo ver la documentación

- **Modelos entidad relación:** abrir cualquier archivo `.dbml` en [dbdiagram.io](https://dbdiagram.io).
- **Contratos de API:** abrir cualquier archivo `.yaml` en [Swagger Editor](https://editor.swagger.io).

## Flujo de trabajo

Cada integrante trabaja en su propia rama (`oswin` y `santiago`). Los cambios llegan a `main` por medio de un pull request que revisa y aprueba el otro integrante.

## Uso de inteligencia artificial

El proyecto usa herramientas de IA generativa como apoyo en todas sus fases. Cada entrega incluye una bitácora que registra cómo se usó la IA, qué se modificó de lo que generó y qué aprendió el equipo.
