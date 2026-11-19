<?php

use Illuminate\Auth\AuthenticationException;
use Illuminate\Foundation\Application;
use Illuminate\Foundation\Configuration\Exceptions;
use Illuminate\Foundation\Configuration\Middleware;
use Illuminate\Http\Exceptions\ThrottleRequestsException;
use Illuminate\Http\Request;
use Illuminate\Validation\ValidationException;
use Symfony\Component\HttpKernel\Exception\NotFoundHttpException;

return Application::configure(basePath: dirname(__DIR__))
    ->withRouting(
        web: __DIR__.'/../routes/web.php',
        api: __DIR__.'/../routes/api.php',
        commands: __DIR__.'/../routes/console.php',
        health: '/up',
    )
    ->withMiddleware(function (Middleware $middleware): void {
        // Los middleware propios registrados
        })
    ->withExceptions(function (Exceptions $exceptions): void {
        // Todo lo que pase por API
        $exceptions->shouldRenderJsonWhen(fn (Request $request) => $request->is('api/*'));

        // Arma el error con el formato
        $error = function (Request $request, string $code, string $message, int $status, array $extra = []) {
            return response()->json(array_merge(
                ['error' => $code, 'message' => $message],
                $extra,
                ['correlation_id' => $request->header('X-Correlation-Id')],
            ), $status);
        };

        // Datos inválidos: 400 
        $exceptions->render(function (ValidationException $e, Request $request) use ($error) {
            if ($request->is('api/*')) {
                return $error($request, 'INVALID_DATA', 'Los datos enviados no son válidos', 400, ['errors' => $e->errors()]);
            }
        });

        // Falta el token o no es válido: 401
        $exceptions->render(function (AuthenticationException $e, Request $request) use ($error) {
            if ($request->is('api/*')) {
                return $error($request, 'UNAUTHENTICATED', 'Debe iniciar sesión para acceder a este recurso', 401);
            }
        });

        // Demasiados intentos seguidos: 429
        $exceptions->render(function (ThrottleRequestsException $e, Request $request) use ($error) {
            if ($request->is('api/*')) {
                return $error($request, 'TOO_MANY_REQUESTS', 'Demasiados intentos, espere un minuto', 429)
                    ->withHeaders($e->getHeaders());
            }
        });

        // Ruta o recurso que no existe: 404
        $exceptions->render(function (NotFoundHttpException $e, Request $request) use ($error) {
            if ($request->is('api/*')) {
                return $error($request, 'NOT_FOUND', 'El recurso solicitado no existe', 404);
            }
        });
    })->create();