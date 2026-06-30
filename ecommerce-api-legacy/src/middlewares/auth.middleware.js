'use strict';

const { config } = require('../config');

// Admin-token auth for destructive/admin endpoints. The header is ALWAYS
// required — a request without a valid Bearer token is rejected (401),
// independent of the dev-only default token value. This is the intentional
// hardening that moves DELETE /api/users/:id from 200 -> 401 (re-baselined).
function requireAdmin(req, res, next) {
  const header = req.get('authorization') || '';
  const token = header.startsWith('Bearer ') ? header.slice(7) : null;
  if (!token || token !== config.adminToken) {
    return res.status(401).json({ error: 'Unauthorized' });
  }
  return next();
}

module.exports = { requireAdmin };
