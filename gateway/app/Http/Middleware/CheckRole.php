<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class CheckRole
{
    public function handle(Request $request, Closure $next, string ...$roles): Response
    {
        $user = $request->user();
        if (! $user || ! $user->hasRole(...$roles)) {
            return response()->json([
                'error' => 'SIN_PERMISO',
                'message' => 'Su rol no tiene permiso para realizar esta operación',
                'correlation_id' => $request->header('X-Correlation-Id'),
            ], 403);
        }
        return $next($request);
    }
}
