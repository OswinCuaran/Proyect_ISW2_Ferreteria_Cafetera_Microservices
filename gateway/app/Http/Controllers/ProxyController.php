<?php

namespace App\Http\Controllers;

use Illuminate\Http\Client\ConnectionException;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Http\Response;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Str;

// Redirige /api/{servicio}/{ruta} al microservicio que corresponde
class ProxyController extends Controller
{
    public function forward(Request $request, string $service, string $path = ''): Response|JsonResponse
    {
        $user = $request->user();
        // 1. Qué permiso exige esta ruta
        $permission = $this->requiredPermission($service, $request->method(), $path);
        if (! $permission || ! $user->hasPermission($permission)) {
            return $this->error('SIN_PERMISO', 'Su rol no tiene permiso para realizar esta operación', 403);
        }
        // 2. Dirección interna del servicio
        $url = rtrim(config("services.microservicios.$service"), '/').'/'.$path;
        // 3. Arma la petición: los filtros de la URL siempre
        $options = ['query' => $request->query()];
        if (! in_array($request->method(), ['GET', 'HEAD'])) {
            $options['json'] = $request->json()->all();
        }
        try {
            $response = Http::withHeaders([
                'X-Internal-Token' => config('services.interno.token'),   // El servicio lo valida
                'X-User-Id' => (string) $user->id,
                'X-User-Role' => $user->role->name,
                'X-User-Warehouse' => (string) ($user->warehouse_id ?? ''),  // Vacío para el Administrador
                'X-Correlation-Id' => $request->header('X-Correlation-Id'),
            ])
                ->acceptJson()
                ->timeout(config('services.interno.timeout'))                // 2 segundos
                ->send($request->method(), $url, $options);
        } catch (ConnectionException) {
            // El servicio está apagado, no existe o tardó más de 2 segundos
            return $this->error('SERVICIO_NO_DISPONIBLE', "El servicio de $service no está disponible en este momento", 503);
        }
        // 4. Devuelve al cliente la respuesta del servicio tal cual llegó
        return response($response->body(), $response->status())
            ->header('Content-Type', $response->header('Content-Type') ?: 'application/json');
    }

    private function requiredPermission(string $service, string $method, string $path): ?string
    {
        $route = $method.' /'.trim($path, '/');
        foreach (config("permissions.$service", []) as $pattern => $permission) {
            if (Str::is($pattern, $route)) {
                return $permission;
            }
        }
        return null;
    }
}