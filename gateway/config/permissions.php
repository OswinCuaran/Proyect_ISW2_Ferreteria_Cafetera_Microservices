<?php

return [
    'inventario' => [
        'GET /warehouses'               => 'inventario.bodegas.consultar',
        'POST /warehouses'              => 'inventario.bodegas.gestionar',
        'PUT /warehouses/*'             => 'inventario.bodegas.gestionar',
        'PATCH /warehouses/*'           => 'inventario.bodegas.gestionar',
        'POST /movements/entries'       => 'inventario.entradas.crear',
        'POST /movements/exits'         => 'inventario.salidas.crear',
        'POST /movements/adjustments'   => 'inventario.ajustes.crear',
        'GET /movements'                => 'inventario.kardex.consultar',
        'POST /transfers'               => 'inventario.traslados.crear',
        'GET /stock/below-minimum'      => 'inventario.bajo_minimo.consultar',
        'PUT /stock/*/*/minimum'        => 'inventario.minimo.configurar',
        'GET /stock/*'                  => 'inventario.stock.consultar',
    ],

    'proveedores' => [
        'GET /*'                        => 'proveedores.consultar',
        'POST /*'                       => 'proveedores.gestionar',
        'PUT /*'                        => 'proveedores.gestionar',
        'PATCH /*'                      => 'proveedores.gestionar',
    ],

    'catalogo' => [
        'GET /products*'                => 'catalogo.productos.consultar',
        'POST /products'                => 'catalogo.productos.gestionar',
        'PUT /products/*'               => 'catalogo.productos.gestionar',
        'PATCH /products/*'             => 'catalogo.productos.gestionar',
        'GET /categories*'              => 'catalogo.categorias.consultar',
        'POST /categories'              => 'catalogo.categorias.gestionar',
        'PUT /categories/*'             => 'catalogo.categorias.gestionar',
        'DELETE /categories/*'          => 'catalogo.categorias.gestionar',
    ],

    'compras' => [
        'GET /orders'                   => 'compras.ordenes.listar',
        'GET /orders/*'                 => 'compras.ordenes.ver',
        'POST /orders'                  => 'compras.ordenes.gestionar',
        'PATCH /orders/*/status'        => 'compras.ordenes.gestionar',
        'POST /orders/*/receptions'     => 'compras.recepciones.crear',
        'GET /returns'                  => 'compras.devoluciones.listar',
        'POST /returns'                 => 'compras.devoluciones.crear',
    ],

    'reportes' => [
        'GET /*'                        => 'reportes.consultar',
    ],
];
