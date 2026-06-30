'use strict';

const express = require('express');
const { Database } = require('./db/database');
const { initDb } = require('./db/seed');

const { UserModel } = require('./models/user.model');
const { CourseModel } = require('./models/course.model');
const { EnrollmentModel } = require('./models/enrollment.model');
const { PaymentModel } = require('./models/payment.model');
const { AuditLogModel } = require('./models/auditLog.model');
const { ReportModel } = require('./models/report.model');

const { CheckoutController } = require('./controllers/checkout.controller');
const { ReportController } = require('./controllers/report.controller');
const { UserController } = require('./controllers/user.controller');

const { buildRouter } = require('./routes');
const { errorHandler } = require('./middlewares/error.middleware');

// Composition root / app factory. Builds the app explicitly — no side effect at
// import time (audit: schema/connection wiring is invoked here, not on require).
async function createApp() {
  const db = new Database();
  await initDb(db);

  const models = {
    userModel: new UserModel(db),
    courseModel: new CourseModel(db),
    enrollmentModel: new EnrollmentModel(db),
    paymentModel: new PaymentModel(db),
    auditLogModel: new AuditLogModel(db),
    reportModel: new ReportModel(db),
  };

  const controllers = {
    checkoutController: new CheckoutController(models),
    reportController: new ReportController(models),
    userController: new UserController(models),
  };

  const app = express();
  app.use(express.json());
  app.use(buildRouter(controllers));
  app.use(errorHandler);

  return { app, db };
}

module.exports = { createApp };
