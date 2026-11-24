<?php

return [
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

    'interno' => [
        'token' => env('INTERNAL_TOKEN'),
        'timeout' => 2,
    ],

    'microservicios' => [
        'inventario'     => env('INVENTARIO_URL'),
        'proveedores'    => env('PROVEEDORES_URL'),
        'catalogo'       => env('CATALOGO_URL'),
        'notificaciones' => env('NOTIFICACIONES_URL'),
        'compras'        => env('COMPRAS_URL'),
        'reportes'       => env('REPORTES_URL'),
    ],

    'admin' => [
        'email' => env('ADMIN_EMAIL'),
        'password' => env('ADMIN_PASSWORD'),
        'security_answer' => env('ADMIN_SECURITY_ANSWER'),
    ],

];
