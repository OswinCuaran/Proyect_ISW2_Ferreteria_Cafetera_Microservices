<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;

class DatabaseSeeder extends Seeder
{
    public function run(): void
    {
        $this->call([
            RoleSeeder::class,             // Primero los roles
            PermissionSeeder::class,       // Los permisos se asignan a roles que ya existen
            SecurityQuestionSeeder::class, // Las preguntas
            UserSeeder::class,             // El Administrador necesita un rol y una pregunta
        ]);
    }
}
