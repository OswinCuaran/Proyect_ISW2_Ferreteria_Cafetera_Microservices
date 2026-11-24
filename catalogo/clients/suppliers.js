class ServiceUnavailableError extends Error {
  constructor(service) {
    super(`El servicio de ${service} no está disponible`);
    this.name = 'ServiceUnavailableError';
    this.service = service;
  }
}

async function getSupplier(id, correlationId) {
  let response;
  try {
    response = await fetch(`${process.env.PROVEEDORES_URL}/${id}`, {
      headers: {
        'X-Internal-Token': process.env.INTERNAL_TOKEN,
        'X-Correlation-Id': correlationId,
      },
      signal: AbortSignal.timeout(2000),
    });
  } catch (err) {
    throw new ServiceUnavailableError('proveedores');
  }
  if (response.status === 404) return null;
  if (!response.ok) throw new ServiceUnavailableError('proveedores');
  return response.json();
}

module.exports = { getSupplier, ServiceUnavailableError };