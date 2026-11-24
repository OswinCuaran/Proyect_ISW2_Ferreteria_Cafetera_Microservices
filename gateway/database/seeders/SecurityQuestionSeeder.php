<?php

namespace Database\Seeders;

use App\Models\SecurityQuestion;
use Illuminate\Database\Seeder;

class SecurityQuestionSeeder extends Seeder
{
    public function run(): void
    {
        $questions = [
            '¿En qué ciudad nació su madre?',
            '¿Cuál fue el nombre de su primera mascota?',
            '¿Cómo se llamaba su escuela primaria?',
            '¿Cuál fue su primer trabajo?',
            '¿Cuál es el nombre de su mejor amigo de la infancia?',
        ];
        foreach ($questions as $question) {
            SecurityQuestion::updateOrCreate(['question' => $question], ['is_active' => true]);
        }
    }
}
