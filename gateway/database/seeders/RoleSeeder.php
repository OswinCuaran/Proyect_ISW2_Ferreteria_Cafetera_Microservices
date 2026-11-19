<?php

namespace Database\Seeders;

use App\Models\Role;
use Illuminate\Database\Seeder;

// Crea los tres roles del sistema
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
            // Busca el rol por nombre: si existe lo actualiza, si no lo crea
            Role::updateOrCreate(['name' => $name], ['description' => $description]);
        }
    }
}