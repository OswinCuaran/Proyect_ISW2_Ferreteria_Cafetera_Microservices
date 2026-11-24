<?php

namespace Database\Seeders;

use App\Models\Permission;
use App\Models\Role;
use Illuminate\Database\Seeder;

class PermissionSeeder extends Seeder
{
    public function run(): void
    {
        $all = ['ADMINISTRADOR', 'OPERADOR', 'VENDEDOR'];
        $adminOperator = ['ADMINISTRADOR', 'OPERADOR'];
        $admin = ['ADMINISTRADOR'];
        $permissions = [
            'usuarios.gestionar'               => ['Registrar, consultar, editar y desactivar usuarios', $admin],
            'roles.consultar'                  => ['Consultar los roles y sus permisos', $admin],
            'inventario.bodegas.consultar'     => ['Consultar las bodegas', $all],
            'inventario.bodegas.gestionar'     => ['Crear, editar y desactivar bodegas', $admin],
            'inventario.entradas.crear'        => ['Registrar entradas de mercancía', $adminOperator],
            'inventario.salidas.crear'         => ['Registrar ventas y salidas', $all],
            'inventario.ajustes.crear'         => ['Registrar ajustes de inventario', $adminOperator],
            'inventario.kardex.consultar'      => ['Consultar el kardex de un producto', $adminOperator],
            'inventario.traslados.crear'       => ['Trasladar productos entre bodegas', $adminOperator],
            'inventario.stock.consultar'       => ['Consultar la disponibilidad de un producto', $all],
            'inventario.bajo_minimo.consultar' => ['Consultar los productos bajo el stock mínimo', $adminOperator],
            'inventario.minimo.configurar'     => ['Configurar el stock mínimo', $admin],
            'proveedores.consultar'            => ['Consultar proveedores y sus contactos', $admin],
            'proveedores.gestionar'            => ['Registrar, editar y dar de baja proveedores y contactos', $admin],
            'catalogo.productos.consultar'     => ['Buscar y consultar productos', $all],
            'catalogo.productos.gestionar'     => ['Crear, editar y dar de baja productos', $admin],
            'catalogo.categorias.consultar'    => ['Consultar categorías y subcategorías', $all],
            'catalogo.categorias.gestionar'    => ['Crear, editar y eliminar categorías', $admin],
            'compras.ordenes.listar'           => ['Listar las órdenes de compra', $admin],
            'compras.ordenes.ver'              => ['Consultar una orden con su detalle', $adminOperator],
            'compras.ordenes.gestionar'        => ['Crear órdenes y cambiar su estado', $admin],
            'compras.recepciones.crear'        => ['Registrar la llegada de mercancía', $adminOperator],
            'compras.devoluciones.listar'      => ['Listar las devoluciones', $admin],
            'compras.devoluciones.crear'       => ['Registrar devoluciones', $adminOperator],
            'reportes.consultar'               => ['Consultar reportes y el dashboard', $admin],
        ];
        $permissionsByRole = [];
        foreach ($permissions as $code => [$description, $roles]) {
            $permission = Permission::updateOrCreate(['code' => $code], ['description' => $description]);
            foreach ($roles as $roleName) {
                $permissionsByRole[$roleName][] = $permission->id;
            }
        }
        foreach ($permissionsByRole as $roleName => $ids) {
            Role::where('name', $roleName)->firstOrFail()->permissions()->sync($ids);
        }
    }
}
