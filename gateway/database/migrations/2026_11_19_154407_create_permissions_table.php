<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

// Tabla PERMISO del modelo ER: cada acción que se puede hacer en el sistema
return new class extends Migration
{
    public function up(): void
    {
        Schema::create('permissions', function (Blueprint $table) {
            $table->increments('id');
            $table->string('code', 80)->unique();             // codigo (ejemplo: inventario.salidas.crear)
            $table->string('description', 150)->nullable();   // descripcion
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('permissions');
    }
};