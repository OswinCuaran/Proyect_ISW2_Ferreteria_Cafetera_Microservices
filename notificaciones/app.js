const express = require('express');
const alertsRouter = require('./routes/alerts');
const internalToken = require('./middleware/internalToken');
const app = express();

app.use(internalToken);
app.use(express.json());

app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'notificaciones' });
});

app.use('/alerts', alertsRouter);

// Ruta que no existe
app.use((req, res) => {
  res.status(404).json({
    error: 'NO_ENCONTRADO',
    message: 'La ruta no existe',
    correlation_id: req.correlationId,
  });
});

// JSON mal formado u otro error inesperado
app.use((err, req, res, next) => {
  if (err.type === 'entity.parse.failed') {
    return res.status(400).json({
      error: 'DATOS_INVALIDOS',
      message: 'El cuerpo no es un JSON válido',
      correlation_id: req.correlationId,
    });
  }
  console.error(`ERROR correlation_id=${req.correlationId}`, err);
  res.status(500).json({
    error: 'ERROR_INTERNO',
    message: 'Error interno del servidor',
    correlation_id: req.correlationId,
  });
});

const port = process.env.PORT || 3000;
app.listen(port, () => console.log(`notificaciones escuchando en el puerto ${port}`));