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
        $middleware->redirectGuestsTo(fn () => null);
        $middleware->api(prepend: [
            \App\Http\Middleware\CorrelationId::class,
        ]);
        $middleware->alias([
            'role' => \App\Http\Middleware\CheckRole::class,
            'internal' => \App\Http\Middleware\VerifyInternalToken::class,
        ]);
    })
    ->withExceptions(function (Exceptions $exceptions): void {
        $exceptions->shouldRenderJsonWhen(fn (Request $request) => $request->is('api/*'));
        $error = function (Request $request, string $code, string $message, int $status, array $extra = []) {
            return response()->json(array_merge(
                ['error' => $code, 'message' => $message],
                $extra,
                ['correlation_id' => $request->header('X-Correlation-Id')],
            ), $status);
        };
        $exceptions->render(function (ValidationException $e, Request $request) use ($error) {
            if ($request->is('api/*')) {
                return $error($request, 'DATOS_INVALIDOS', 'Los datos enviados no son válidos', 400, ['errors' => $e->errors()]);
            }
        });
        $exceptions->render(function (AuthenticationException $e, Request $request) use ($error) {
            if ($request->is('api/*')) {
                return $error($request, 'NO_AUTENTICADO', 'Debe iniciar sesión para acceder a este recurso', 401);
            }
        });
        $exceptions->render(function (ThrottleRequestsException $e, Request $request) use ($error) {
            if ($request->is('api/*')) {
                return $error($request, 'DEMASIADOS_INTENTOS', 'Demasiados intentos, espere un minuto', 429)
                    ->withHeaders($e->getHeaders());
            }
        });
        $exceptions->render(function (NotFoundHttpException $e, Request $request) use ($error) {
            if ($request->is('api/*')) {
                return $error($request, 'NO_ENCONTRADO', 'El recurso solicitado no existe', 404);
            }
        });
    })->create();
