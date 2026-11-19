<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Casts\Attribute;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Foundation\Auth\User as Authenticatable;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Str;
use Laravel\Sanctum\HasApiTokens;

// Modelo de la tabla users
class User extends Authenticatable
{
    // HasApiTokens: permite crear y revocar los tokens de Sanctum
    use HasApiTokens;
    protected $fillable = [
        'role_id',
        'security_question_id',
        'warehouse_id',
        'document_type',
        'document_number',
        'first_name',
        'last_name',
        'email',
        'password',
        'security_answer',
        'is_active',
        'last_login_at',
    ];

    // Nunca se devuelven en las respuestas JSON
    protected $hidden = [
        'password',
        'security_answer',
    ];

    protected function casts(): array
    {
        return [
            'password' => 'hashed',          // Se guarda con hash automáticamente
            'is_active' => 'boolean',
            'last_login_at' => 'datetime',
        ];
    }

    // La respuesta de seguridad se guarda en minúsculas, sin espacios a los lados y con hash.
    protected function securityAnswer(): Attribute
    {
        return Attribute::make(
            set: fn (string $value) => Hash::make(Str::lower(trim($value))),
        );
    }

    // Compara la respuesta que escribe el usuario con la guardada
    public function checkSecurityAnswer(string $answer): bool
    {
        return Hash::check(Str::lower(trim($answer)), $this->security_answer);
    }

    // Revisa si el usuario tiene alguno de los roles indicados (lo usará el middleware de roles)
    public function hasRole(string ...$roles): bool
    {
        return in_array($this->role->name, $roles);
    }

    // Cada usuario tiene un rol
    public function role(): BelongsTo
    {
        return $this->belongsTo(Role::class);
    }

    // Cada usuario escogió una pregunta de seguridad
    public function securityQuestion(): BelongsTo
    {
        return $this->belongsTo(SecurityQuestion::class);
    }
}