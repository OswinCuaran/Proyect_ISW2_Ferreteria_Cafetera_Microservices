<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

// Tabla ROL_PERMISO del modelo ER: entidad débil que une roles y permisos (muchos a muchos)
return new class extends Migration
{
    public function up(): void
    {
        Schema::create('permission_role', function (Blueprint $table) {
            $table->unsignedInteger('role_id');               // rol_id, mismo tipo que roles.id
            $table->unsignedInteger('permission_id');         // permiso_id, mismo tipo que permissions.id
            // Llave primaria compuesta: un rol no puede tener el mismo permiso dos veces
            $table->primary(['role_id', 'permission_id']);
            // Si se borra un rol o un permiso, se borran sus asignaciones
            $table->foreign('role_id')->references('id')->on('roles')->cascadeOnDelete();
            $table->foreign('permission_id')->references('id')->on('permissions')->cascadeOnDelete();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('permission_role');
    }
};
