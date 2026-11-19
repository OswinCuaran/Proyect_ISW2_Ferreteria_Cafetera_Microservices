<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

// Modelo de la tabla security_questions
class SecurityQuestion extends Model
{
    public $timestamps = false;
    protected $fillable = ['question', 'is_active'];
    protected function casts(): array
    {
        return [
            'is_active' => 'boolean',
        ];
    }

    // Una pregunta la pueden haber escogido muchos usuarios
    public function users(): HasMany
    {
        return $this->hasMany(User::class);
    }
}