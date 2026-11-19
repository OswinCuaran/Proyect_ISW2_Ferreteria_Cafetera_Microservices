<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;
use Illuminate\Database\Eloquent\Relations\HasMany;

// Modelo de la tabla roles
class Role extends Model
{
    public $timestamps = false;

    // Campos que se pueden llenar con create() o update()
    protected $fillable = ['name', 'description'];

    // Un rol tiene muchos permisos y un permiso está en muchos roles
    public function permissions(): BelongsToMany
    {
        return $this->belongsToMany(Permission::class);
    }

    // Un rol lo tienen muchos usuarios
    public function users(): HasMany
    {
        return $this->hasMany(User::class);
    }
}