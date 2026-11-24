const express = require('express');
const internalToken = require('./middleware/internalToken');
const pool = require('./db');
const categoriesRouter = require('./routes/categories');
const productsRouter = require('./routes/products');
const app = express();

app.use(internalToken);
app.use(express.json());
app.use('/categories', categoriesRouter);
app.use('/products', productsRouter);
app.get('/health', (req, res) => res.json({ status: 'ok', service: 'catalogo' }));

app.use((req, res) => {
  res.status(404).json({
    error: 'NO_ENCONTRADO',
    message: 'La ruta no existe',
    correlation_id: req.correlationId,
  });
});

app.use((err, req, res, next) => {
  if (err.type === 'entity.parse.failed') {
    return res.status(400).json({
      error: 'DATOS_INVALIDOS',
      message: 'El cuerpo de la petición no es un JSON válido',
      correlation_id: req.correlationId,
    });
  }
  if (err.name === 'ServiceUnavailableError') {
    console.error(`${err.message} correlation_id=${req.correlationId}`);
    return res.status(503).json({
      error: 'SERVICIO_NO_DISPONIBLE',
      message: `El servicio de ${err.service} no está disponible en este momento`,
      correlation_id: req.correlationId,
    });
  }
  console.error(`Error inesperado correlation_id=${req.correlationId}`, err);
  res.status(500).json({
    error: 'ERROR_INTERNO',
    message: 'Ocurrió un error inesperado',
    correlation_id: req.correlationId,
  });
});

pool.query('SELECT 1')
  .then(() => console.log('Conexión a MySQL correcta'))
  .catch((err) => console.error('No se pudo conectar a MySQL:', err.message));

app.listen(3000, '0.0.0.0', () => console.log('Catálogo escuchando en el puerto 3000'));