<?php

use App\Http\Controllers\AuthController;
use App\Http\Controllers\RoleController;
use App\Http\Controllers\SecurityQuestionController;
use App\Http\Controllers\UserController;
use Illuminate\Support\Facades\Route;

Route::middleware('throttle:10,1')->group(function () {
    Route::post('/login', [AuthController::class, 'login']);
    Route::get('/password/question', [AuthController::class, 'securityQuestion']);
    Route::post('/password/recover', [AuthController::class, 'recoverPassword']);
});

Route::middleware('auth:sanctum')->group(function () {
    Route::post('/logout', [AuthController::class, 'logout']);
    Route::get('/me', [AuthController::class, 'me']);
    Route::put('/password', [AuthController::class, 'changePassword']);

    // Rutas solo para el Administrador
    Route::middleware('role:ADMINISTRADOR')->group(function () {
        Route::post('/register', [UserController::class, 'register']);
        Route::get('/users', [UserController::class, 'index']);
        Route::put('/users/{user}', [UserController::class, 'update']);
        Route::patch('/users/{user}/deactivate', [UserController::class, 'deactivate']);
        Route::patch('/users/{user}/activate', [UserController::class, 'activate']);
        Route::get('/roles', [RoleController::class, 'index']);
        Route::get('/security-questions', [SecurityQuestionController::class, 'index']);
    });
});

// Rutas internas: solo para los microservicios, con el token interno
Route::middleware('internal')->prefix('internal')->group(function () {
    // Notificaciones la usa para saber a quién avisar
    Route::get('/users', [UserController::class, 'index']);
});