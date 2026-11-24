<?php

namespace Database\Seeders;

use App\Models\Role;
use Illuminate\Database\Seeder;

class RoleSeeder extends Seeder
{
    public function run(): void
    {
        $roles = [
            'ADMINISTRADOR' => 'Gestiona usuarios, catálogo, proveedores, compras y reportes de todas las bodegas',
            'OPERADOR'      => 'Registra entradas, salidas, ajustes, traslados y recepciones en su bodega',
            'VENDEDOR'      => 'Registra ventas y consulta productos y disponibilidad',
        ];
        foreach ($roles as $name => $description) {
            Role::updateOrCreate(['name' => $name], ['description' => $description]);
        }
    }
}
