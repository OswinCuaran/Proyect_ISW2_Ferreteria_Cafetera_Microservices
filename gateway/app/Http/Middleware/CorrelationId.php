<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Str;
use Symfony\Component\HttpFoundation\Response;

// Le da a cada petición un identificador único (X-Correlation-Id) para seguirla
// por el Gateway y los microservicios, y deja un registro de la petición en el log
class CorrelationId
{
    public function handle(Request $request, Closure $next): Response
    {
        // Si la petición ya trae uno (por ejemplo, de otro servicio) se conserva. Si no, se crea
        $correlationId = $request->header('X-Correlation-Id') ?: (string) Str::uuid();
        // Se guarda en la petición para que los controladores y los errores lo puedan leer
        $request->headers->set('X-Correlation-Id', $correlationId);
        // Todo lo que se escriba en el log durante esta petición llevará el identificador
        Log::withContext(['correlation_id' => $correlationId]);
        $start = microtime(true);
        // Aquí la petición sigue hacia los demás middleware y el controlador
        $response = $next($request);
        // De regreso: el cliente también recibe el identificador en la respuesta
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