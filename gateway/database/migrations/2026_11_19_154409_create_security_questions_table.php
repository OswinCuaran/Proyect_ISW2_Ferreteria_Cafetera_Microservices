<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

// Tabla PREGUNTA_SEGURIDAD del modelo ER: preguntas para recuperar la contraseña
return new class extends Migration
{
    public function up(): void
    {
        Schema::create('security_questions', function (Blueprint $table) {
            $table->increments('id');
            $table->string('question', 150)->unique();        // pregunta
            $table->boolean('is_active')->default(true);      // activa, permite retirar una pregunta sin borrarla
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('security_questions');
    }
};
