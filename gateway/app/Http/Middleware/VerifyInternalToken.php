<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class VerifyInternalToken
{
    public function handle(Request $request, Closure $next): Response
    {
        $expected = config('services.interno.token');
        $received = $request->header('X-Internal-Token');
        if (blank($expected) || blank($received) || ! hash_equals($expected, $received)) {
            return response()->json([
                'error' => 'TOKEN_INTERNO_INVALIDO',
                'message' => 'Esta ruta solo la pueden usar los microservicios del sistema',
                'correlation_id' => $request->header('X-Correlation-Id'),
            ], 401);
        }
        return $next($request);
    }
}
