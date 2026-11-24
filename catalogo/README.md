# Microservicio de Catálogo

Administra los productos que vende la ferretería, organizados en categorías y subcategorías. Los demás servicios solo guardan el id del producto y le preguntan a Catálogo por su nombre, su precio o si sigue activo.

## Tecnología

| | |
|---|---|
| Lenguaje | JavaScript (Node.js) |
| Framework | Express |
| Base de datos | `catalogo_db` (MySQL) |
| Puerto del contenedor | 3000 |
| Nombre del contenedor | `catalogo` (`http://catalogo:3000`, en tu equipo `http://localhost:3001`) |

## Funcionalidades

- Registro, consulta y actualización de productos, con su código, unidad de medida, precio de venta, categoría y proveedor.
- Búsqueda de productos por nombre o código y filtros por categoría, proveedor o estado.
- Baja de productos sin borrarlos, para conservar su historial.
- Gestión de categorías y subcategorías.

## Se comunica con

- **Proveedores:** antes de guardar un producto revisa que su proveedor exista y esté activo.
- Lo llaman **Inventario**, para validar que un producto exista y esté activo antes de moverlo, y **Reportes**, para obtener el nombre, la categoría y el precio de los productos.

## Rutas

Todas exigen el header `X-Internal-Token`, salvo `/health`. A través del Gateway van con el prefijo `/api/catalogo`. Los tres roles pueden consultar productos y categorías; crearlos, editarlos, darlos de baja o eliminarlos solo lo hace el Administrador.

| Método | Ruta | Qué hace |
|---|---|---|
| GET | `/health` | Estado del servicio |
| GET | `/products?search=&category_id=&supplier_id=&is_active=` | Busca y filtra productos |
| GET | `/products/{id}` | Consulta un producto |
| POST | `/products` | Registra un producto |
| PUT | `/products/{id}` | Actualiza un producto |
| PATCH | `/products/{id}/deactivate` | Da de baja un producto |
| GET | `/categories?parent_category_id=` | Lista las categorías o las subcategorías de una categoría |
| POST | `/categories` | Crea una categoría |
| PUT | `/categories/{id}` | Actualiza una categoría |
| DELETE | `/categories/{id}` | Elimina una categoría |

Un producto tiene `code`, `name`, `description`, `category_id`, `supplier_id`, `unit_of_measure` y `sale_price`. La unidad de medida puede ser `UNIDAD`, `PAR`, `CAJA`, `METRO`, `ROLLO`, `KILOGRAMO`, `BULTO`, `LITRO` o `GALON`. Una categoría tiene `name`, `description` y `parent_category_id` cuando es una subcategoría.

## Reglas de negocio

- El código de un producto y el nombre de una categoría no se pueden repetir: responde `409 DUPLICADO`.
- Un producto solo se guarda si su proveedor existe y está activo. Si Proveedores no responde, responde `503 SERVICIO_NO_DISPONIBLE` y no guarda nada.
- Un producto dado de baja no se borra, pero Inventario ya no le registra movimientos.
- Una categoría que tiene productos o subcategorías no se puede eliminar: responde `409 CATEGORIA_EN_USO`.

## Cómo levantarlo

```bash
docker compose up -d --build catalogo
docker logs -f catalogo
```

Las tablas se crean con `database/init.sql` la primera vez que arranca su base de datos.

## Requisitos que cubre

REQ-F-005 y REQ-F-006.

## Documentación

- Contrato de API: [`docs/Entrega_2/contratos_api/catalogo.YAML`](../docs/Entrega_2/contratos_api/catalogo.YAML)
- Modelo de datos: [`docs/Entrega_2/codigos_dbml/catalogo_db.dbml`](../docs/Entrega_2/codigos_dbml/catalogo_db.dbml)
