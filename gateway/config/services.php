<?php

return [

    /*
    |--------------------------------------------------------------------------
    | Third Party Services
    |--------------------------------------------------------------------------
    |
    | This file is for storing the credentials for third party services such
    | as Resend, Postmark, AWS, and more. This file provides the de facto
    | location for this type of information, allowing packages to have
    | a conventional file to locate the various service credentials.
    |
    */

    'postmark' => [
        'key' => env('POSTMARK_API_KEY'),
    ],

    'resend' => [
        'key' => env('RESEND_API_KEY'),
    ],

    'ses' => [
        'key' => env('AWS_ACCESS_KEY_ID'),
        'secret' => env('AWS_SECRET_ACCESS_KEY'),
        'region' => env('AWS_DEFAULT_REGION', 'us-east-1'),
    ],

    'slack' => [
        'notifications' => [
            'bot_user_oauth_token' => env('SLACK_BOT_USER_OAUTH_TOKEN'),
            'channel' => env('SLACK_BOT_USER_DEFAULT_CHANNEL'),
        ],
    ],

    // Token compartido entre el Gateway y los microservicios
    'interno' => [
        'token' => env('INTERNAL_TOKEN'),
        'timeout' => 2,   // Segundos máximos de espera al llamar a un servicio
    ],

    // Dirección de cada microservicio dentro de la red de Docker o de Kubernetes
    'microservicios' => [
        'inventario'     => env('INVENTARIO_URL'),
        'proveedores'    => env('PROVEEDORES_URL'),
        'catalogo'       => env('CATALOGO_URL'),
        'notificaciones' => env('NOTIFICACIONES_URL'),
        'compras'        => env('COMPRAS_URL'),
        'reportes'       => env('REPORTES_URL'),
    ],

    // Datos del primer Administrador, los usa el UserSeeder
    'admin' => [
        'email' => env('ADMIN_EMAIL'),
        'password' => env('ADMIN_PASSWORD'),
        'security_answer' => env('ADMIN_SECURITY_ANSWER'),
    ],

];
