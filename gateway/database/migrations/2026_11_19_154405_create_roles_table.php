<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

// Tabla ROL del modelo ER: los tres roles del sistema
return new class extends Migration
{
    public function up(): void
    {
        Schema::create('roles', function (Blueprint $table) {
            $table->increments('id');                         
            $table->string('name', 30)->unique();             // ER: nombre (ADMINISTRADOR, OPERADOR o VENDEDOR)
            $table->string('description', 150)->nullable();   // ER: descripcion
        });
    }
    public function down(): void
    {
        Schema::dropIfExists('roles');
    }
};