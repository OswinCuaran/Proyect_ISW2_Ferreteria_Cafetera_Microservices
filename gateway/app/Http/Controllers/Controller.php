<?php

namespace App\Http\Controllers;

use Illuminate\Http\JsonResponse;

abstract class Controller
{
    protected function error(string $code, string $message, int $status): JsonResponse
    {
        return response()->json([
            'error' => $code,
            'message' => $message,
            'correlation_id' => request()->header('X-Correlation-Id'),
        ], $status);
    }
}
