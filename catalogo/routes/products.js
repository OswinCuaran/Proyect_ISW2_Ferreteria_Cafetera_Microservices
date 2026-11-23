const express = require('express');
const pool = require('../db');
const { getSupplier } = require('../clients/suppliers');
const { sendError, wrap, parseId } = require('../utils/errors');
const router = express.Router();
const UNITS = ['UNIDAD', 'PAR', 'CAJA', 'METRO', 'ROLLO', 'KILOGRAMO', 'BULTO', 'LITRO', 'GALON'];
const SELECT_PRODUCT = `
  SELECT p.*, c.name AS category
  FROM products p JOIN categories c ON c.id = p.category_id`;

function formatProduct(row) {
  return {
    id: row.id,
    code: row.code,
    name: row.name,
    description: row.description,
    category_id: row.category_id,
    category: row.category,
    supplier_id: row.supplier_id,
    unit_of_measure: row.unit_of_measure,
    sale_price: row.sale_price,
    is_active: Boolean(row.is_active),
  };
}

async function findProduct(id) {
  const [rows] = await pool.query(`${SELECT_PRODUCT} WHERE p.id = ?`, [id]);
  return rows[0] || null;
}

async function categoryExists(id) {
  const [rows] = await pool.query('SELECT id FROM categories WHERE id = ?', [id]);
  return rows.length > 0;
}

async function validateBody(body) {
  const errors = {};
  const { code, name, description, category_id, supplier_id, unit_of_measure, sale_price } = body;

  if (typeof code !== 'string' || code.trim() === '' || code.length > 30) {
    errors.code = 'El codigo es obligatorio (maximo 30 caracteres)';
  }
  if (typeof name !== 'string' || name.trim() === '' || name.length > 150) {
    errors.name = 'El nombre es obligatorio (maximo 150 caracteres)';
  }
  if (description != null && typeof description !== 'string') {
    errors.description = 'La descripcion debe ser texto';
  }
  if (!Number.isInteger(category_id) || category_id < 1) {
    errors.category_id = 'La categoria es obligatoria (numero entero)';
  } else if (!(await categoryExists(category_id))) {
    errors.category_id = 'La categoria no existe';
  }
  if (!Number.isInteger(supplier_id) || supplier_id < 1) {
    errors.supplier_id = 'El proveedor es obligatorio (numero entero)';
  }
  if (!UNITS.includes(unit_of_measure)) {
    errors.unit_of_measure = `Debe ser una de: ${UNITS.join(', ')}`;
  }
  if (typeof sale_price !== 'number' || sale_price < 0) {
    errors.sale_price = 'Debe ser un numero mayor o igual a 0';
  }
  return errors;
}
// Validacion de los datos
async function validateProduct(req) {
  const errors = await validateBody(req.body);
  if (!errors.supplier_id) {
    const supplier = await getSupplier(req.body.supplier_id, req.correlationId);
    if (!supplier) {
      errors.supplier_id = 'El proveedor no existe';
    } else if (!supplier.is_active) {
      errors.supplier_id = 'El proveedor esta dado de baja';
    }
  }
  return errors;
}
const invalid = (req, res, errors) =>
  sendError(req, res, 400, 'DATOS_INVALIDOS', 'Los datos enviados no son validos', errors);
const notFound = (req, res) =>
  sendError(req, res, 404, 'NO_ENCONTRADO', 'El producto no existe');

// GET /products?search=&category_id=&supplier_id=&is_active=
router.get('/', wrap(async (req, res) => {
  const { search, category_id, supplier_id, is_active } = req.query;
  const where = [];
  const params = [];
  if (search) {
    where.push('(p.name LIKE ? OR p.code LIKE ?)');
    params.push(`%${search}%`, `%${search}%`);
  }
  if (category_id) {
    where.push('p.category_id = ?');
    params.push(category_id);
  }
  if (supplier_id) {
    where.push('p.supplier_id = ?');
    params.push(supplier_id);
  }
  if (is_active !== undefined) {
    where.push('p.is_active = ?');
    params.push(is_active === 'true' ? 1 : 0);
  }
  const sql = `${SELECT_PRODUCT} ${where.length ? 'WHERE ' + where.join(' AND ') : ''} ORDER BY p.id`;
  const [rows] = await pool.query(sql, params);
  res.json(rows.map(formatProduct));
}));

//obtener por el id
router.get('/:id', wrap(async (req, res) => {
  const id = parseId(req.params.id);
  const product = id && await findProduct(id);
  if (!product) return notFound(req, res);
  res.json(formatProduct(product));
}));

//subir producto
router.post('/', wrap(async (req, res) => {
  const errors = await validateProduct(req);
  if (Object.keys(errors).length) return invalid(req, res, errors);
  const { name, description, category_id, supplier_id, unit_of_measure, sale_price } = req.body;
  const code = req.body.code.trim();
  const [dup] = await pool.query('SELECT id FROM products WHERE code = ?', [code]);
  if (dup.length) {
    return sendError(req, res, 409, 'DUPLICADO', `Ya existe un producto con el codigo ${code}`);
  }
  const [result] = await pool.query(
    `INSERT INTO products (code, name, description, category_id, supplier_id, unit_of_measure, sale_price)
     VALUES (?, ?, ?, ?, ?, ?, ?)`,
    [code, name.trim(), description ?? null, category_id, supplier_id, unit_of_measure, sale_price],
  );
  res.status(201).json(formatProduct(await findProduct(result.insertId)));
}));

//put por id
router.put('/:id', wrap(async (req, res) => {
  const id = parseId(req.params.id);
  if (!id || !(await findProduct(id))) return notFound(req, res);
  const errors = await validateProduct(req);
  if (Object.keys(errors).length) return invalid(req, res, errors);
  const { name, description, category_id, supplier_id, unit_of_measure, sale_price } = req.body;
  const code = req.body.code.trim();
  const [dup] = await pool.query('SELECT id FROM products WHERE code = ? AND id <> ?', [code, id]);
  if (dup.length) {
    return sendError(req, res, 409, 'DUPLICADO', `Ya existe un producto con el codigo ${code}`);
  }
  await pool.query(
    `UPDATE products SET code = ?, name = ?, description = ?, category_id = ?,
       supplier_id = ?, unit_of_measure = ?, sale_price = ? WHERE id = ?`,
    [code, name.trim(), description ?? null, category_id, supplier_id, unit_of_measure, sale_price, id],
  );
  res.json(formatProduct(await findProduct(id)));
}));

router.patch('/:id/deactivate', wrap(async (req, res) => {
  const id = parseId(req.params.id);
  if (!id || !(await findProduct(id))) return notFound(req, res);

  // Baja logica: no se borra para conservar el historial
  await pool.query('UPDATE products SET is_active = 0 WHERE id = ?', [id]);
  res.json(formatProduct(await findProduct(id)));
}));

module.exports = router;