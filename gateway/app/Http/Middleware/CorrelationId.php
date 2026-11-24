<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Str;
use Symfony\Component\HttpFoundation\Response;

class CorrelationId
{
    public function handle(Request $request, Closure $next): Response
    {
        $correlationId = $request->header('X-Correlation-Id') ?: (string) Str::uuid();
        $request->headers->set('X-Correlation-Id', $correlationId);
        Log::withContext(['correlation_id' => $correlationId]);
        $start = microtime(true);
        $response = $next($request);
        $response->headers->set('X-Correlation-Id', $correlationId);
        Log::info('Petición atendida', [
            'method' => $request->method(),
            'path' => $request->path(),
            'status' => $response->getStatusCode(),
            'duration_ms' => round((microtime(true) - $start) * 1000),
            'user_id' => $request->user()?->id,
        ]);
        return $response;
    }
}
