# Microservicio de Catálogo

Administra los productos que vende la ferretería, organizados en categorías y subcategorías.

## Tecnología

| | |
|---|---|
| Lenguaje | JavaScript (Node.js) |
| Framework | Express |
| Base de datos | `catalogo_db` (MySQL) |
| Puerto del contenedor | 3000 |
| Nombre en Kubernetes | `catalogo` (`http://catalogo:3000`) |

## Funcionalidades

- Registro, consulta y actualización de productos, con su código, unidad de medida, precio de venta, categoría y proveedor.
- Búsqueda y filtrado de productos por nombre, código, categoría o proveedor.
- Baja de productos sin borrarlos, para conservar su historial.
- Gestión de categorías y subcategorías.

## Se comunica con

- **Proveedores:** valida que el proveedor del producto exista y esté activo.
- Lo llaman **Inventario** y **Compras**, para validar productos, y **Reportes**, para consultar precios y categorías.

## Requisitos que cubre

REQ-F-005 y REQ-F-006.

## Documentación

- Contrato de API: [`docs/Entrega_2/contratos_api/catalogo.YAML`](../docs/Entrega_2/contratos_api/catalogo.YAML)
- Modelo de datos: [`docs/Entrega_2/codigos_dbml/catalogo_db.dbml`](../docs/Entrega_2/codigos_dbml/catalogo_db.dbml)
