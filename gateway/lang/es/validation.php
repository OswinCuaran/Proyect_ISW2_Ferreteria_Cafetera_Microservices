<?php

return [
    'required' => 'El campo :attribute es obligatorio.',
    'email' => 'El campo :attribute debe ser un correo válido.',
    'string' => 'El campo :attribute debe ser un texto.',
    'integer' => 'El campo :attribute debe ser un número entero.',
    'boolean' => 'El campo :attribute debe ser verdadero o falso.',
    'min' => [
        'string' => 'El campo :attribute debe tener al menos :min caracteres.',
        'numeric' => 'El campo :attribute debe ser mínimo :min.',
    ],
    'max' => [
        'string' => 'El campo :attribute no debe tener más de :max caracteres.',
        'numeric' => 'El campo :attribute no debe ser mayor que :max.',
    ],
    'different' => 'El campo :attribute debe ser diferente de :other.',
    'unique' => 'El :attribute ya está registrado.',
    'exists' => 'El :attribute seleccionado no existe.',
    'in' => 'El :attribute seleccionado no es válido.',

    'attributes' => [
        'email' => 'correo',
        'password' => 'contraseña',
        'current_password' => 'contraseña actual',
        'new_password' => 'nueva contraseña',
        'security_answer' => 'respuesta de seguridad',
        'document_type' => 'tipo de documento',
        'document_number' => 'número de documento',
        'first_name' => 'nombre',
        'last_name' => 'apellido',
        'role_id' => 'rol',
        'warehouse_id' => 'bodega',
        'security_question_id' => 'pregunta de seguridad',
    ],
];