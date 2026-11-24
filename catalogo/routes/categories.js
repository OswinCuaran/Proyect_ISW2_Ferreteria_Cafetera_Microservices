const express = require('express');
const pool = require('../db');
const { sendError, wrap, parseId } = require('../utils/errors');

const router = express.Router();

function formatCategory(row) {
  return {
    id: row.id,
    name: row.name,
    description: row.description,
    parent_category_id: row.parent_category_id,
    is_active: Boolean(row.is_active),
  };
}

async function findCategory(id) {
  const [rows] = await pool.query('SELECT * FROM categories WHERE id = ?', [id]);
  return rows[0] || null;
}

async function validateBody(body) {
  const errors = {};
  const { name, parent_category_id: parentId } = body;
  if (typeof name !== 'string' || name.trim() === '' || name.length > 100) {
    errors.name = 'El nombre es obligatorio (máximo 100 caracteres)';
  }
  if (parentId != null && !(await findCategory(parentId))) {
    errors.parent_category_id = 'La categoría padre no existe';
  }
  return errors;
}

const invalid = (req, res, errors) =>
  sendError(req, res, 400, 'DATOS_INVALIDOS', 'Los datos enviados no son válidos', errors);

router.get('/', wrap(async (req, res) => {
  const parentId = req.query.parent_category_id;
  const [rows] = parentId
    ? await pool.query('SELECT * FROM categories WHERE parent_category_id = ? ORDER BY id', [parentId])
    : await pool.query('SELECT * FROM categories ORDER BY id');
  res.json(rows.map(formatCategory));
}));

router.post('/', wrap(async (req, res) => {
  const errors = await validateBody(req.body);
  if (Object.keys(errors).length) return invalid(req, res, errors);
  const name = req.body.name.trim();
  const [dup] = await pool.query('SELECT id FROM categories WHERE name = ?', [name]);
  if (dup.length) {
    return sendError(req, res, 409, 'DUPLICADO', `Ya existe una categoría con el nombre ${name}`);
  }
  const [result] = await pool.query(
    'INSERT INTO categories (name, description, parent_category_id) VALUES (?, ?, ?)',
    [name, req.body.description ?? null, req.body.parent_category_id ?? null],
  );
  res.status(201).json({ message: 'Categoría registrada correctamente', category: formatCategory(await findCategory(result.insertId)) });
}));

router.put('/:id', wrap(async (req, res) => {
  const id = parseId(req.params.id);
  if (!id || !(await findCategory(id))) {
    return sendError(req, res, 404, 'NO_ENCONTRADO', 'La categoría no existe');
  }
  const errors = await validateBody(req.body);
  if (Object.keys(errors).length) return invalid(req, res, errors);
  const name = req.body.name.trim();
  const [dup] = await pool.query('SELECT id FROM categories WHERE name = ? AND id <> ?', [name, id]);
  if (dup.length) {
    return sendError(req, res, 409, 'DUPLICADO', `Ya existe una categoría con el nombre ${name}`);
  }
  await pool.query(
    'UPDATE categories SET name = ?, description = ?, parent_category_id = ? WHERE id = ?',
    [name, req.body.description ?? null, req.body.parent_category_id ?? null, id],
  );
  res.json({ message: 'Categoría actualizada correctamente', category: formatCategory(await findCategory(id)) });
}));

router.delete('/:id', wrap(async (req, res) => {
  const id = parseId(req.params.id);
  if (!id || !(await findCategory(id))) {
    return sendError(req, res, 404, 'NO_ENCONTRADO', 'La categoría no existe');
  }
  const [[{ used }]] = await pool.query(
    `SELECT (SELECT COUNT(*) FROM products WHERE category_id = ?)
          + (SELECT COUNT(*) FROM categories WHERE parent_category_id = ?) AS used`,
    [id, id],
  );
  if (used > 0) {
    return sendError(req, res, 409, 'CATEGORIA_EN_USO',
      'No se puede eliminar porque tiene productos o subcategorías asociados');
  }
  await pool.query('DELETE FROM categories WHERE id = ?', [id]);
  res.json({ message: 'Categoría eliminada correctamente' });
}));

module.exports = router;