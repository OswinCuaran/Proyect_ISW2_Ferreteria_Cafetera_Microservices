<?php

use App\Http\Controllers\AuthController;
use Illuminate\Support\Facades\Route;

// Rutas públicas
Route::middleware('throttle:10,1')->group(function () {
    Route::post('/login', [AuthController::class, 'login']);
    Route::get('/password/question', [AuthController::class, 'securityQuestion']);
    Route::post('/password/recover', [AuthController::class, 'recoverPassword']);
});

// Rutas protegidas: necesitan el token de Sanctum en el header Authorization
Route::middleware('auth:sanctum')->group(function () {
    Route::post('/logout', [AuthController::class, 'logout']);
    Route::get('/me', [AuthController::class, 'me']);
    Route::put('/password', [AuthController::class, 'changePassword']);
});