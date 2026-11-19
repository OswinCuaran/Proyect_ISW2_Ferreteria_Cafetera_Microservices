<?php

namespace App\Http\Controllers;

use App\Http\Resources\UserResource;
use App\Models\User;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Http\Response;
use Illuminate\Support\Facades\Hash;

// Autenticación: login, logout, usuario de la sesión y contraseña
class AuthController extends Controller
{
    // POST /api/login (pública)
    public function login(Request $request): JsonResponse
    {
        // Si falta un campo, Laravel responde 400
        $data = $request->validate([
            'email' => ['required', 'email'],
            'password' => ['required', 'string'],
        ]);

        $user = User::with('role')->where('email', $data['email'])->first();

        // Mismo mensaje si el correo no existe o si la contraseña está mal
        if (! $user || ! Hash::check($data['password'], $user->password)) {
            return $this->error('INVALID_CREDENTIALS', 'El correo o la contraseña no son correctos', 401);
        }

        if (! $user->is_active) {
            return $this->error('INACTIVE_USER', 'El usuario está desactivado', 403);
        }

        $user->update(['last_login_at' => now()]);

        // Crea el token de Sanctum. Se guarda con hash
        $token = $user->createToken('api')->plainTextToken;

        return response()->json([
            'token' => $token,
            'token_type' => 'Bearer',
            'user' => new UserResource($user),
        ]);
    }

    // POST /api/logout
    public function logout(Request $request): Response
    {
        // Borra solo el token con el que se hizo esta petición
        $request->user()->currentAccessToken()->delete();

        return response()->noContent(); // 204
    }

    // GET /api/me
    public function me(Request $request): JsonResponse
    {
        return response()->json(new UserResource($request->user()->load('role')));
    }

    public function securityQuestion(Request $request): JsonResponse
    {
        $data = $request->validate([
            'email' => ['required', 'email'],
        ]);

        $user = User::with('securityQuestion')
            ->where('email', $data['email'])
            ->where('is_active', true)
            ->first();

        if (! $user) {
            return $this->error('NOT_FOUND', 'No existe un usuario activo con ese correo', 404);
        }

        return response()->json(['question' => $user->securityQuestion->question]);
    }

    // POST /api/password/recover
    public function recoverPassword(Request $request): Response|JsonResponse
    {
        $data = $request->validate([
            'email' => ['required', 'email'],
            'security_answer' => ['required', 'string'],
            'new_password' => ['required', 'string', 'min:8'],
        ]);

        $user = User::where('email', $data['email'])->where('is_active', true)->first();

        // Compara lo que escribió el usuario con la respuesta guardada
        if (! $user || ! $user->checkSecurityAnswer($data['security_answer'])) {
            return $this->error('INVALID_SECURITY_ANSWER', 'La respuesta de seguridad no es correcta', 401);
        }

        $user->update(['password' => $data['new_password']]); // El modelo le aplica el hash

        // Cierra todas las sesiones abiertas, por si alguien más tenía acceso
        $user->tokens()->delete();

        return response()->noContent(); // 204
    }

    // PUT /api/password
    public function changePassword(Request $request): Response|JsonResponse
    {
        $data = $request->validate([
            'current_password' => ['required', 'string'],
            'new_password' => ['required', 'string', 'min:8', 'different:current_password'],
        ]);

        $user = $request->user();

        // 400 y no 401: el usuario sí está autenticado, lo que está mal es el dato
        if (! Hash::check($data['current_password'], $user->password)) {
            return $this->error('INVALID_CURRENT_PASSWORD', 'La contraseña actual no es correcta', 400);
        }

        $user->update(['password' => $data['new_password']]);
        $user->tokens()->where('id', '!=', $user->currentAccessToken()->id)->delete();

        return response()->noContent();
    }
}