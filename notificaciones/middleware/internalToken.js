const crypto = require('crypto');

function internalToken(req, res, next) {
  const correlationId = req.get('X-Correlation-Id') || crypto.randomUUID();
  req.correlationId = correlationId;
  res.set('X-Correlation-Id', correlationId);
  console.log(`${req.method} ${req.originalUrl} correlation_id=${correlationId}`);

  if (req.path === '/health') return next();

  const expected = Buffer.from(process.env.INTERNAL_TOKEN || '');
  const received = Buffer.from(req.get('X-Internal-Token') || '');
  if (!expected.length || expected.length !== received.length || !crypto.timingSafeEqual(expected, received)) {
    return res.status(401).json({
      error: 'TOKEN_INTERNO_INVALIDO',
      message: 'Esta ruta solo la puede usar el API Gateway',
      correlation_id: correlationId,
    });
  }
  next();
}

module.exports = internalToken;