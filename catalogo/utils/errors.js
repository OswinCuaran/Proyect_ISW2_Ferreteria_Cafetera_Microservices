// Respuesta de error con el formato comun de todos los servicios
function sendError(req, res, status, code, message, errors) {
  const body = { error: code, message, correlation_id: req.correlationId };
  if (errors) body.errors = errors;
  return res.status(status).json(body);
}

// Express 4 no atrapa los errores de las funciones async: este envoltorio los manda al manejador de errores
const wrap = (fn) => (req, res, next) => Promise.resolve(fn(req, res, next)).catch(next);

// Convierte un valor de la URL en id entero; devuelve null si no es valido
function parseId(value) {
  const id = Number(value);
  return Number.isInteger(id) && id >= 1 ? id : null;
}

module.exports = { sendError, wrap, parseId };