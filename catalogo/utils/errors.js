function sendError(req, res, status, code, message, errors) {
  const body = { error: code, message, correlation_id: req.correlationId };
  if (errors) body.errors = errors;
  return res.status(status).json(body);
}

const wrap = (fn) => (req, res, next) => Promise.resolve(fn(req, res, next)).catch(next);

function parseId(value) {
  const id = Number(value);
  return Number.isInteger(id) && id >= 1 ? id : null;
}

module.exports = { sendError, wrap, parseId };