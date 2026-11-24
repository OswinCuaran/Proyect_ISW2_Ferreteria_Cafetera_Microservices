<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('users', function (Blueprint $table) {
            $table->id();
            $table->unsignedInteger('role_id');
            $table->unsignedInteger('security_question_id');
            $table->unsignedInteger('warehouse_id')->nullable();
            $table->enum('document_type', ['CC', 'CE', 'PA']);
            $table->string('document_number', 20);
            $table->string('first_name', 100);
            $table->string('last_name', 100);
            $table->string('email', 120)->unique();
            $table->string('password');
            $table->string('security_answer');
            $table->boolean('is_active')->default(true);
            $table->timestamp('last_login_at')->nullable();
            $table->timestamps();
            $table->unique(['document_type', 'document_number']);
            $table->foreign('role_id')->references('id')->on('roles')->restrictOnDelete();
            $table->foreign('security_question_id')->references('id')->on('security_questions')->restrictOnDelete();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('users');
    }
};
