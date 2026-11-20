<?php

namespace Database\Seeders;

use App\Models\Role;
use App\Models\SecurityQuestion;
use App\Models\User;
use Illuminate\Database\Seeder;
use RuntimeException;

// Crea el primer Administrador, que después crea las cuentas de los demás
class UserSeeder extends Seeder
{
    public function run(): void
    {
        
        $admin = config('services.admin');
        if (blank($admin['email']) || blank($admin['password']) || blank($admin['security_answer'])) {
            throw new RuntimeException('Faltan ADMIN_EMAIL, ADMIN_PASSWORD o ADMIN_SECURITY_ANSWER en el .env del gateway');
        }
        User::updateOrCreate(
            ['email' => $admin['email']],
            [
                'role_id' => Role::where('name', 'ADMINISTRADOR')->value('id'),
                'security_question_id' => SecurityQuestion::orderBy('id')->value('id'), // La primera pregunta
                'warehouse_id' => null,                         // El Administrador ve todas las bodegas
                'document_type' => 'CC',
                'document_number' => '1000000001',
                'first_name' => 'Administrador',
                'last_name' => 'General',
                'password' => $admin['password'],               // El modelo le aplica el hash
                'security_answer' => $admin['security_answer'], // El modelo la normaliza y le aplica el hash
                'is_active' => true,
            ]
        );
    }
}