<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;

// Modelo de la tabla permissions
class Permission extends Model
{
    public $timestamps = false;
    protected $fillable = ['code', 'description'];
    
    // Relación inversa: los roles que tienen este permiso
    public function roles(): BelongsToMany
    {
        return $this->belongsToMany(Role::class);
    }
}