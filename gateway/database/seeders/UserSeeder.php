<?php

namespace Database\Seeders;

use App\Models\Role;
use App\Models\SecurityQuestion;
use App\Models\User;
use Illuminate\Database\Seeder;
use RuntimeException;

class UserSeeder extends Seeder
{
    public function run(): void
    {
        $admin = config('services.admin');
        if (blank($admin['email']) || blank($admin['password']) || blank($admin['security_answer'])) {
            throw new RuntimeException('Faltan ADMIN_EMAIL, ADMIN_PASSWORD o ADMIN_SECURITY_ANSWER en el .env del gateway');
        }
        User::firstOrCreate(
            ['email' => $admin['email']],
            [
                'role_id' => Role::where('name', 'ADMINISTRADOR')->value('id'),
                'security_question_id' => SecurityQuestion::orderBy('id')->value('id'),
                'warehouse_id' => null,
                'document_type' => 'CC',
                'document_number' => '1000000001',
                'first_name' => 'Administrador',
                'last_name' => 'General',
                'password' => $admin['password'],
                'security_answer' => $admin['security_answer'],
                'is_active' => true,
            ]
        );
    }
}
