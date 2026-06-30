'use strict';

const crypto = require('crypto');

// Adaptive password hashing via Node stdlib scrypt (salted), replacing the
// homemade `badCrypto` (audit: CRITICAL weak/home-rolled hash). Stored format:
//   scrypt$<saltHex>$<derivedKeyHex>
// scrypt is used over bcrypt to avoid native-build friction.
const KEYLEN = 64;

function hash(plain) {
  const salt = crypto.randomBytes(16);
  const derived = crypto.scryptSync(String(plain), salt, KEYLEN);
  return `scrypt$${salt.toString('hex')}$${derived.toString('hex')}`;
}

function verify(plain, stored) {
  if (typeof stored !== 'string' || !stored.startsWith('scrypt$')) return false;
  const [, saltHex, hashHex] = stored.split('$');
  const salt = Buffer.from(saltHex, 'hex');
  const expected = Buffer.from(hashHex, 'hex');
  const derived = crypto.scryptSync(String(plain), salt, KEYLEN);
  return derived.length === expected.length && crypto.timingSafeEqual(derived, expected);
}

module.exports = { hash, verify };
