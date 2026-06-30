'use strict';

// Minimal configurable logger replacing ad-hoc console.log (audit: LOW).
// Honors LOG_LEVEL; silent in tests when LOG_LEVEL=silent.
const LEVELS = { silent: 0, error: 1, warn: 2, info: 3, debug: 4 };
const current = LEVELS[process.env.LOG_LEVEL] ?? LEVELS.info;

function at(level, args) {
  if (LEVELS[level] <= current) {
    // eslint-disable-next-line no-console
    (level === 'error' ? console.error : console.log)(`[${level}]`, ...args);
  }
}

module.exports = {
  info: (...a) => at('info', a),
  warn: (...a) => at('warn', a),
  error: (...a) => at('error', a),
  debug: (...a) => at('debug', a),
};
