'use strict';

const sqlite3 = require('sqlite3').verbose();
const { promisify } = require('util');

// Thin async wrapper over the sqlite3 callback driver (audit: deprecated
// callback API / callback hell). Models depend on this; no SQL leaks above.
class Database {
  constructor() {
    this.raw = new sqlite3.Database(':memory:');
    this.get = promisify(this.raw.get.bind(this.raw));
    this.all = promisify(this.raw.all.bind(this.raw));
  }

  // `run` is wrapped manually so callers can read `lastID`/`changes`
  // (promisify would drop the `this` RunResult context).
  run(sql, params = []) {
    return new Promise((resolve, reject) => {
      this.raw.run(sql, params, function (err) {
        if (err) return reject(err);
        resolve({ lastID: this.lastID, changes: this.changes });
      });
    });
  }

  exec(sql) {
    return promisify(this.raw.exec.bind(this.raw))(sql);
  }
}

module.exports = { Database };
