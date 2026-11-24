const GATEWAY_URL = process.env.GATEWAY_URL || 'http://gateway:8000';

async function getUsers(role, warehouseId, correlationId) {
  const params = new URLSearchParams({ role });
  if (warehouseId) params.set('warehouse_id', warehouseId);
  const response = await fetch(`${GATEWAY_URL}/api/internal/users?${params}`, {
    headers: {
      'X-Internal-Token': process.env.INTERNAL_TOKEN,
      'X-Correlation-Id': correlationId,
      Accept: 'application/json',
    },
    signal: AbortSignal.timeout(2000),
  });
  if (!response.ok) throw new Error(`Gateway respondió ${response.status}`);
  const body = await response.json();
  return Array.isArray(body) ? body : body.data || [];
}

async function getRecipients(warehouseId, correlationId) {
  const [operators, admins] = await Promise.all([
    getUsers('OPERADOR', warehouseId, correlationId),
    getUsers('ADMINISTRADOR', null, correlationId),
  ]);
  const emails = [...operators, ...admins]
    .filter((user) => user.email && user.is_active !== false)
    .map((user) => user.email);
  return [...new Set(emails)];
}

module.exports = { getRecipients };