# Microservicio de Proveedores

Administra los proveedores a los que la ferretería les compra, con sus datos de contacto y su tiempo de entrega.

## Tecnología

| | |
|---|---|
| Lenguaje | Python |
| Framework | Django |
| Base de datos | `proveedores_db` (MySQL) |
| Puerto del contenedor | 8000 |
| Nombre en Kubernetes | `proveedores` (`http://proveedores:8000`) |

## Funcionalidades

- Registro, consulta y actualización de proveedores. El NIT no se puede repetir.
- Baja de proveedores sin borrarlos, para conservar su historial.
- Gestión de las personas de contacto de cada proveedor.

## Se comunica con

No llama a otros servicios. Lo llaman **Catálogo** y **Compras** para validar que un proveedor exista y esté activo.

## Requisitos que cubre

REQ-F-004.

## Documentación

- Contrato de API: [`docs/Entrega_2/contratos_api/proveedores.YAML`](../docs/Entrega_2/contratos_api/proveedores.YAML)
- Modelo de datos: [`docs/Entrega_2/codigos_dbml/proveedores_db.dbml`](../docs/Entrega_2/codigos_dbml/proveedores_db.dbml)
