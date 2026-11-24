const express = require('express');
const { getRecipients } = require('../clients/gateway');
const { sendMail } = require('../utils/mailer');
const router = express.Router();
const REQUIRED = ['product_id', 'warehouse_id', 'current_quantity', 'minimum_stock'];

function validate(body) {
  const errors = [];
  for (const field of REQUIRED) {
    if (body[field] === undefined || body[field] === null || body[field] === '') {
      errors.push(`${field} es obligatorio`);
    }
  }
  if (errors.length) return errors;
  if (!Number.isInteger(body.product_id) || body.product_id < 1) errors.push('product_id debe ser un entero positivo');
  if (!Number.isInteger(body.warehouse_id) || body.warehouse_id < 1) errors.push('warehouse_id debe ser un entero positivo');
  if (body.product_code != null && typeof body.product_code !== 'string') errors.push('product_code debe ser texto');
  if (body.product_name != null && typeof body.product_name !== 'string') errors.push('product_name debe ser texto');
  if (typeof body.current_quantity !== 'number' || body.current_quantity < 0) errors.push('current_quantity debe ser un número mayor o igual a 0');
  if (typeof body.minimum_stock !== 'number' || body.minimum_stock < 0) errors.push('minimum_stock debe ser un número mayor o igual a 0');
  return errors;
}

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function withRetries(task, correlationId) {
  for (let attempt = 1; attempt <= 3; attempt++) {
    try {
      return await task();
    } catch (err) {
      console.error(`ERROR intento ${attempt}/3 correlation_id=${correlationId}: ${err.message}`);
      if (attempt === 3) throw err;
      await sleep(attempt * 1000);
    }
  }
}

async function processAlert(alert, correlationId) {
  try {
    const recipients = await withRetries(() => getRecipients(alert.warehouse_id, correlationId), correlationId);
    if (recipients.length === 0) {
      console.warn(`ADVERTENCIA sin destinatarios para la bodega ${alert.warehouse_id} correlation_id=${correlationId}`);
      return;
    }
    const product = alert.product_name ? `${alert.product_code} - ${alert.product_name}` : `${alert.product_id}`;
    const warehouse = alert.warehouse || alert.warehouse_id;
    const subject = `Stock bajo: ${alert.product_name || 'producto ' + alert.product_id} (${warehouse})`;
    const text =
      `El producto ${product} quedó por debajo del stock mínimo.\n\n` +
      `Bodega: ${warehouse}\n` +
      `Cantidad actual: ${alert.current_quantity}\n` +
      `Stock mínimo: ${alert.minimum_stock}\n\n` +
      `Se recomienda reabastecer pronto.`;
    await withRetries(() => sendMail({ to: recipients, subject, text }, correlationId), correlationId);
    console.log(`Alerta enviada a ${recipients.length} destinatario(s) correlation_id=${correlationId}`);
  } catch (err) {
    console.error(`ERROR no se pudo enviar la alerta correlation_id=${correlationId}: ${err.message}`);
  }
}

router.post('/', (req, res) => {
  const errors = validate(req.body || {});
  if (errors.length) {
    return res.status(400).json({
      error: 'DATOS_INVALIDOS',
      message: errors.join('; '),
      correlation_id: req.correlationId,
    });
  }
  res.status(202).json({ message: 'Alerta recibida' });
  processAlert(req.body, req.correlationId);
});

module.exports = router;