'use strict';

const express = require('express');
const { requireAdmin } = require('../middlewares/auth.middleware');
const { asyncHandler } = require('../middlewares/error.middleware');

// View layer: maps METHOD /path -> controller. No business logic here.
function buildRouter({ checkoutController, reportController, userController }) {
  const router = express.Router();

  router.post('/api/checkout', asyncHandler(checkoutController.checkout));
  router.get('/api/admin/financial-report', asyncHandler(reportController.financial));

  // Destructive: guarded by admin auth (intentional 200 -> 401 for callers
  // without a valid token).
  router.delete('/api/users/:id', requireAdmin, asyncHandler(userController.remove));

  return router;
}

module.exports = { buildRouter };
