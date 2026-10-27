# Sistema de Gestión de Inventarios - Ferretería Cafetera

Proyecto de aula de **Ingeniería de Software II** de la Universidad Nacional de Colombia, sede Manizales.

Sistema de gestión de inventarios basado en una arquitectura de microservicios para Ferretería Cafetera, una pyme distribuidora de materiales de construcción con sede principal en Manizales y bodegas en Pereira y Armenia. El sistema reemplaza el kardex manual de la empresa, descuenta el inventario en el momento de cada venta, permite consultar la disponibilidad en las tres sedes y genera alertas cuando un producto baja de su stock mínimo.

## Equipo

- Oswin Olsman Cuaran Cuaran
- Santiago Lopez

**Docente:** Albeiro Montes

## Arquitectura

![Arquitectura de microservicios](docs/entrega_2/Arquitectura_y_Modelos_ER.jpg)

Todas las peticiones entran por un API Gateway propio, que valida el token de Sanctum y el rol del usuario y redirige cada petición al microservicio que corresponde. Los microservicios se comunican entre sí por medio de API REST y se ubican por su nombre gracias al DNS interno de Kubernetes. Cada servicio administra únicamente su propia base de datos.

| Componente | Framework | Base de datos |
|---|---|---|
| API Gateway (usuarios y autenticación) | Laravel + Sanctum | gateway_db |
| Inventario | Django | inventario_db |
| Proveedores | Django | proveedores_db |
| Catálogo | Express | catalogo_db |
| Compras y devoluciones | Flask | compras_db |
| Notificaciones y alertas | Express | Sin base de datos |
| Reportes y dashboard | Flask | Sin base de datos |

Notificaciones y Reportes son servicios sin estado: no guardan información propia y consultan a los demás servicios lo que necesitan.

## Tecnologías

- **Backend:** Laravel (PHP), Django y Flask (Python), Express (Node.js)
- **Base de datos:** MySQL
- **Contenedores y orquestación:** Docker y Kubernetes
- **Pruebas:** Thunder Client y Locust
- **Documentación:** OpenAPI (Swagger) y dbdiagram.io

## Estructura del repositorio

```
docs/
├── entrega_1/                                   Investigación, requisitos y bitácora de IA
└── entrega_2/
    ├── imagenes/                                Imágenes de los modelos entidad relación
    ├── codigos_dbml/                            Código de los modelos entidad relación
    ├── contratos_api/                           Contratos de API en formato OpenAPI
    ├── Segunda_Entrega_Proyecto_de_Software_2.pdf   Documento de la entrega
    ├── Bitacora_IA_Entrega2.xlsx                Bitácora de uso de IA
    └── Arquitectura_y_modelos_ER.jpg            Diagrama de arquitectura
```

## Cómo ver la documentación

- **Modelos entidad relación:** abrir cualquier archivo `.dbml` en [dbdiagram.io](https://dbdiagram.io).
- **Contratos de API:** abrir cualquier archivo `.yaml` en [Swagger Editor](https://editor.swagger.io).

## Flujo de trabajo

Cada integrante trabaja en su propia rama (`oswin` y `santiago`). Los cambios llegan a `main` por medio de un pull request que revisa y aprueba el otro integrante.

## Uso de inteligencia artificial

El proyecto usa herramientas de IA generativa como apoyo en todas sus fases. Cada entrega incluye una bitácora que registra cómo se usó la IA, qué se modificó de lo que generó y qué aprendió el equipo.
