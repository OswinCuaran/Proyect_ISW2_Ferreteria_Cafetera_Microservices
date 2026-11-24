<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Casts\Attribute;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Foundation\Auth\User as Authenticatable;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Str;
use Laravel\Sanctum\HasApiTokens;

class User extends Authenticatable
{
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

    protected $hidden = [
        'password',
        'security_answer',
    ];

    protected function casts(): array
    {
        return [
            'password' => 'hashed',
            'is_active' => 'boolean',
            'last_login_at' => 'datetime',
        ];
    }

    protected function securityAnswer(): Attribute
    {
        return Attribute::make(
            set: fn (string $value) => Hash::make(Str::lower(trim($value))),
        );
    }

    public function checkSecurityAnswer(string $answer): bool
    {
        return Hash::check(Str::lower(trim($answer)), $this->security_answer);
    }

    public function hasRole(string ...$roles): bool
    {
        return in_array($this->role->name, $roles);
    }

    public function hasPermission(string $code): bool
    {
        return $this->role->permissions->contains('code', $code);
    }

    public function role(): BelongsTo
    {
        return $this->belongsTo(Role::class);
    }

    public function securityQuestion(): BelongsTo
    {
        return $this->belongsTo(SecurityQuestion::class);
    }
}
