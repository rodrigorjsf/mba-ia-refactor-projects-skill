#!/usr/bin/env node
/**
 * Characterization harness for ecommerce-api-legacy.
 *
 * Generated from the Phase-1 route map. Boots the app on a free port in the
 * background, waits until it answers, then hits every mapped endpoint with a
 * minimal valid payload and records, per endpoint:
 *   { method, path, status_class, top_keys }
 *
 * Modes:
 *   capture  -> write harness/baseline.json (the contract)
 *   verify   -> re-run and compare against the baseline; GREEN if the status
 *               CLASS (2xx/4xx/5xx) is identical for every endpoint. Top-level
 *               body keys are compared loosely (informational; removal of
 *               sensitive fields such as `pass`/`senha`/`password` is tolerated).
 *
 * Usage: node harness/run.js [capture|verify]
 */
const { spawn } = require('child_process');
const net = require('net');
const http = require('http');
const fs = require('fs');
const path = require('path');

const PROJECT_DIR = path.resolve(__dirname, '..');
const ENTRY = path.join(PROJECT_DIR, 'src', 'app.js');
const BASELINE = path.join(__dirname, 'baseline.json');

const SENSITIVE_KEYS = ['pass', 'password', 'senha', 'pwd', 'card', 'cc', 'gatewayKey'];

// Route map (method + path) with a minimal valid payload for mutations.
// Derived from src/AppManager.setupRoutes + api.http.
const REQUESTS = [
  {
    name: 'POST /api/checkout',
    method: 'POST',
    path: '/api/checkout',
    // minimal fields that pass the handler validation (u,e,cid,cc) with an
    // approved card (starts with "4") and an active course (id 2 = Docker).
    body: { usr: 'HarnessUser', eml: 'harness@example.com', pwd: 'senhaforte', c_id: 2, card: '4111222233334444' },
  },
  {
    name: 'GET /api/admin/financial-report',
    method: 'GET',
    path: '/api/admin/financial-report',
  },
  {
    name: 'DELETE /api/users/:id',
    method: 'DELETE',
    path: '/api/users/2',
    // Admin token is read from env; the harness sends NONE on purpose so the
    // baseline characterizes the unauthenticated caller. Post-hardening this
    // endpoint is expected to move 200 -> 401 (intentional, re-baselined).
  },
];

function getFreePort() {
  return new Promise((resolve, reject) => {
    // Prefer 3000 (the legacy hardcoded port) when free; otherwise an ephemeral one.
    const tryPort = (port) => {
      const srv = net.createServer();
      srv.once('error', () => {
        if (port === 3000) {
          const s2 = net.createServer();
          s2.once('error', reject);
          s2.listen(0, () => { const p = s2.address().port; s2.close(() => resolve(p)); });
        } else reject(new Error('no free port'));
      });
      srv.listen(port, () => { const p = srv.address().port; srv.close(() => resolve(p)); });
    };
    tryPort(3000);
  });
}

function waitForServer(port, timeoutMs = 8000) {
  const start = Date.now();
  return new Promise((resolve, reject) => {
    const poll = () => {
      // Any HTTP response (incl. 404) means the server is up and listening.
      const req = http.request({ host: '127.0.0.1', port, path: '/', method: 'GET' }, (res) => {
        res.resume();
        resolve();
      });
      req.on('error', () => {
        if (Date.now() - start > timeoutMs) return reject(new Error('server did not start in time'));
        setTimeout(poll, 150);
      });
      req.end();
    };
    poll();
  });
}

function call(port, r) {
  return new Promise((resolve) => {
    const payload = r.body ? JSON.stringify(r.body) : null;
    const headers = {};
    if (payload) {
      headers['Content-Type'] = 'application/json'; // without this Express yields 415 -> falsifies baseline
      headers['Content-Length'] = Buffer.byteLength(payload);
    }
    const req = http.request({ host: '127.0.0.1', port, path: r.path, method: r.method, headers }, (res) => {
      let data = '';
      res.on('data', (c) => (data += c));
      res.on('end', () => {
        let topKeys = [];
        try {
          const parsed = JSON.parse(data);
          if (Array.isArray(parsed)) {
            // array response: characterize the element shape (top keys of first item)
            topKeys = parsed.length && parsed[0] && typeof parsed[0] === 'object'
              ? Object.keys(parsed[0]).sort() : ['<array>'];
          } else if (parsed && typeof parsed === 'object') {
            topKeys = Object.keys(parsed).sort();
          } else {
            topKeys = ['<scalar>'];
          }
        } catch (_) {
          topKeys = ['<text>']; // plain-text body (e.g. res.send("..."))
        }
        resolve({
          name: r.name,
          method: r.method,
          path: r.path,
          status: res.statusCode,
          status_class: `${Math.floor(res.statusCode / 100)}xx`,
          top_keys: topKeys,
        });
      });
    });
    req.on('error', () => resolve({
      name: r.name, method: r.method, path: r.path,
      status: 0, status_class: 'ERR', top_keys: [],
    }));
    if (payload) req.write(payload);
    req.end();
  });
}

async function boot(port) {
  const child = spawn(process.execPath, [ENTRY], {
    cwd: PROJECT_DIR,
    env: { ...process.env, PORT: String(port) },
    stdio: ['ignore', 'pipe', 'pipe'],
  });
  let log = '';
  child.stdout.on('data', (d) => (log += d));
  child.stderr.on('data', (d) => (log += d));
  child._log = () => log;
  return child;
}

async function run(mode) {
  const port = await getFreePort();
  const child = await boot(port);
  let results;
  try {
    await waitForServer(port);
    results = [];
    for (const r of REQUESTS) results.push(await call(port, r));
  } catch (e) {
    console.error('Harness boot failed:', e.message);
    console.error(child._log());
    child.kill('SIGKILL');
    process.exit(1);
  }
  child.kill('SIGKILL');

  if (mode === 'capture') {
    fs.writeFileSync(BASELINE, JSON.stringify({ generatedAt: new Date().toISOString(), port: 'free', endpoints: results }, null, 2));
    console.log('=== BASELINE CAPTURED ===');
    for (const r of results) console.log(`${r.status_class} (${r.status})  ${r.name}  top_keys=${JSON.stringify(r.top_keys)}`);
    console.log(`\nWrote ${BASELINE}`);
    const fivexx = results.filter((r) => r.status_class === '5xx' || r.status_class === 'ERR');
    if (fivexx.length) { console.error('Unexpected 5xx/ERR in baseline:', fivexx.map((r) => r.name)); process.exit(1); }
    return;
  }

  // verify
  const baseline = JSON.parse(fs.readFileSync(BASELINE, 'utf8'));
  const byName = Object.fromEntries(baseline.endpoints.map((e) => [e.name, e]));
  let red = false;
  console.log('=== HARNESS VERIFY ===');
  for (const r of results) {
    const base = byName[r.name];
    if (!base) { console.log(`?  ${r.name}: not in baseline`); continue; }
    const statusOk = r.status_class === base.status_class;
    // loose body diff: only sensitive-field removals are tolerated; report the rest
    const removed = base.top_keys.filter((k) => !r.top_keys.includes(k));
    const added = r.top_keys.filter((k) => !base.top_keys.includes(k));
    const removedNonSensitive = removed.filter((k) => !SENSITIVE_KEYS.includes(k));
    const bodyNote = (removed.length || added.length)
      ? `  body Δ removed=${JSON.stringify(removed)} added=${JSON.stringify(added)}` : '';
    const mark = statusOk ? 'GREEN' : 'RED  ';
    if (!statusOk) red = true;
    console.log(`${mark} ${r.name}  base=${base.status_class}(${base.status}) now=${r.status_class}(${r.status})${bodyNote}`);
    if (removedNonSensitive.length) console.log(`      note: non-sensitive top keys removed: ${JSON.stringify(removedNonSensitive)} (loose diff; nested fields not seen)`);
  }
  console.log(red ? '\nRESULT: RED (status-class regression)' : '\nRESULT: GREEN (status class preserved on every endpoint)');
  process.exit(red ? 1 : 0);
}

run(process.argv[2] || 'capture');
