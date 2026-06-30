'use strict';

// Configuration and secrets come from the environment. Dev-only defaults are
// clearly marked so the app boots with one command, but NO real production
// secret is embedded in source (see audit: CRITICAL "segredos hardcoded").
const config = {
  port: parseInt(process.env.PORT, 10) || 3000,
  nodeEnv: process.env.NODE_ENV || 'development',

  // Secrets: read from env; dev fallbacks are obvious non-secrets.
  dbUser: process.env.DB_USER || 'dev-db-user',
  dbPass: process.env.DB_PASS || 'dev-only-change-me',
  paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || 'dev-only-payment-key',
  smtpUser: process.env.SMTP_USER || 'no-reply@example.com',

  // Admin token guards destructive endpoints. Dev default exists so the app
  // runs locally, but the auth middleware ALWAYS requires the header — a
  // request with no token is rejected regardless of this default.
  adminToken: process.env.ADMIN_TOKEN || 'dev-only-admin-token',
};

module.exports = { config };
