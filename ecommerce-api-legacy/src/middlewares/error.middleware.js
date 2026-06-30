'use strict';

const logger = require('../logger');

// Centralized error handling (audit: MEDIUM). Handlers stop hand-rolling 500s;
// the internal detail is logged, never leaked to the client.
// eslint-disable-next-line no-unused-vars
function errorHandler(err, req, res, next) {
  logger.error('unhandled error:', err && err.message);
  if (res.headersSent) return next(err);
  return res.status(500).json({ error: 'Erro interno' });
}

// Wrap an async handler so rejected promises reach the error middleware.
function asyncHandler(fn) {
  return (req, res, next) => Promise.resolve(fn(req, res, next)).catch(next);
}

module.exports = { errorHandler, asyncHandler };
