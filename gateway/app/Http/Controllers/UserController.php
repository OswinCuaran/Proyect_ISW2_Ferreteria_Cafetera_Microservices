<?php

namespace App\Http\Controllers;

use App\Http\Resources\UserResource;
use App\Models\Role;
use App\Models\User;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Validation\ValidationException;

class UserController extends Controller
{
    public function register(Request $request): JsonResponse
    {
        $data = $request->validate([
            'document_type' => ['required', 'in:CC,CE,PA'],
            'document_number' => ['required', 'string', 'max:20'],
            'first_name' => ['required', 'string', 'max:100'],
            'last_name' => ['required', 'string', 'max:100'],
            'email' => ['required', 'email', 'max:120'],
            'password' => ['required', 'string', 'min:8'],
            'role_id' => ['required', 'integer', 'exists:roles,id'],
            'warehouse_id' => ['nullable', 'integer', 'min:1'],
            'security_question_id' => ['required', 'integer', 'exists:security_questions,id'],
            'security_answer' => ['required', 'string', 'max:100'],
        ]);
        if (User::where('email', $data['email'])->exists()) {
            return $this->error('CORREO_DUPLICADO', 'Ya existe un usuario con ese correo', 409);
        }
        if (User::where('document_type', $data['document_type'])->where('document_number', $data['document_number'])->exists()) {
            return $this->error('DOCUMENTO_DUPLICADO', 'Ya existe un usuario con ese documento', 409);
        }
        $data['warehouse_id'] = $this->warehouseFor($data['role_id'], $data['warehouse_id'] ?? null);
        $user = User::create($data);
        return response()->json([
            'message' => 'Usuario registrado correctamente',
            'user' => new UserResource($user->fresh('role')),
        ], 201);
    }

    public function index(Request $request): JsonResponse
    {
        $users = User::with('role')
            ->when($request->query('role'), fn ($query, $role) => $query->whereHas('role', fn ($r) => $r->where('name', $role)))
            ->when($request->query('warehouse_id'), fn ($query, $warehouseId) => $query->where('warehouse_id', $warehouseId))
            ->when($request->has('is_active'), fn ($query) => $query->where('is_active', $request->boolean('is_active')))
            ->orderBy('first_name')
            ->get();
        return response()->json(UserResource::collection($users));
    }

    public function update(Request $request, User $user): JsonResponse
    {
        $data = $request->validate([
            'first_name' => ['sometimes', 'required', 'string', 'max:100'],
            'last_name' => ['sometimes', 'required', 'string', 'max:100'],
            'email' => ['sometimes', 'required', 'email', 'max:120'],
            'role_id' => ['sometimes', 'required', 'integer', 'exists:roles,id'],
            'warehouse_id' => ['sometimes', 'nullable', 'integer', 'min:1'],
        ]);
        if (isset($data['email']) && User::where('email', $data['email'])->where('id', '!=', $user->id)->exists()) {
            return $this->error('CORREO_DUPLICADO', 'Ya existe un usuario con ese correo', 409);
        }
        if (isset($data['role_id']) && $user->id === $request->user()->id && (int) $data['role_id'] !== $user->role_id) {
            return $this->error('OPERACION_NO_PERMITIDA', 'No puede cambiar su propio rol', 400);
        }
        $data['warehouse_id'] = $this->warehouseFor(
            $data['role_id'] ?? $user->role_id,
            array_key_exists('warehouse_id', $data) ? $data['warehouse_id'] : $user->warehouse_id,
        );
        $user->update($data);
        return response()->json([
            'message' => 'Usuario actualizado correctamente',
            'user' => new UserResource($user->fresh('role')),
        ]);
    }

    public function deactivate(Request $request, User $user): JsonResponse
    {
        if ($user->id === $request->user()->id) {
            return $this->error('OPERACION_NO_PERMITIDA', 'No puede desactivar su propia cuenta', 400);
        }
        $user->update(['is_active' => false]);
        $user->tokens()->delete();
        return response()->json([
            'message' => 'Usuario desactivado correctamente',
            'user' => new UserResource($user->load('role')),
        ]);
    }

    public function activate(User $user): JsonResponse
    {
        $user->update(['is_active' => true]);
        return response()->json([
            'message' => 'Usuario activado correctamente',
            'user' => new UserResource($user->load('role')),
        ]);
    }

    private function warehouseFor(int $roleId, ?int $warehouseId): ?int
    {
        $role = Role::findOrFail($roleId);
        if ($role->name === 'ADMINISTRADOR') {
            return null;
        }
        if (! $warehouseId) {
            throw ValidationException::withMessages([
                'warehouse_id' => 'El Operador y el Vendedor deben tener una bodega asignada.',
            ]);
        }
        return $warehouseId;
    }
}
