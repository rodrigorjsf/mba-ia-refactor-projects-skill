'use strict';

const { config } = require('../config');
const logger = require('../logger');

// Payment authorization isolated behind a stubbable service (audit: HIGH naive
// security validation + business effect in controller). The approval heuristic
// is PRESERVED (card prefix "4") to keep the characterization contract green,
// but it is now quarantined here with a clear TODO rather than inlined in the
// HTTP handler. The gateway key never reaches logs (audit: CRITICAL secret in log).
const APPROVED_CARD_PREFIX = '4';

function authorize(cardNumber, amount) {
  // NOTE: placeholder authorization — replace with a real gateway call.
  // The gateway key stays server-side and is never logged; only a masked
  // PAN suffix is traced.
  const maskedPan = `****${String(cardNumber).slice(-4)}`;
  logger.info(`payment.authorize pan=${maskedPan} amount=${amount}`);
  const approved = String(cardNumber).startsWith(APPROVED_CARD_PREFIX);
  return { status: approved ? 'PAID' : 'DENIED', gatewayKeyPresent: Boolean(config.paymentGatewayKey) };
}

module.exports = { authorize };
