"""Characterization harness for task-manager-api.

Boots the Flask app on a free port (self-initializing schema + seed, so it does
NOT depend on import-time side effects), hits every endpoint in the route map,
and records {method, path, status_class, top_keys} per endpoint.

Usage:
    python harness/characterize.py <out.json>          # capture
    python harness/characterize.py <out.json> --compare <baseline.json>
"""
import json
import os
import socket
import sys
import threading
import time

import requests
from werkzeug.serving import make_server

# Import the app + db at module level (must stay importable after the refactor).
from app import app, db
from seed import seed_data

# Sensitive top-level fields that are allowed to disappear post-refactor.
SENSITIVE_FIELDS = {"password", "senha", "secret_key", "token_secret"}

# Route map: (method, path, json_body). Ordered: GETs, login, then mutations,
# so re-seeded data stays consistent across the run. DELETEs target rows that no
# earlier GET in this run reads (tasks/10, users/3, categories/4).
ROUTES = [
    ("GET", "/", None),
    ("GET", "/health", None),
    ("GET", "/tasks", None),
    ("GET", "/tasks/1", None),
    ("GET", "/tasks/search?q=a", None),
    ("GET", "/tasks/stats", None),
    ("GET", "/users", None),
    ("GET", "/users/1", None),
    ("GET", "/users/1/tasks", None),
    ("GET", "/reports/summary", None),
    ("GET", "/reports/user/1", None),
    ("GET", "/categories", None),
    ("POST", "/login", {"email": "joao@email.com", "password": "1234"}),
    ("POST", "/tasks", {"title": "Harness task"}),
    ("POST", "/users", {"name": "Harness User", "email": "harness@example.com",
                         "password": "abcd", "role": "user"}),
    ("POST", "/categories", {"name": "Harness Category"}),
    ("PUT", "/tasks/1", {"status": "done"}),
    ("PUT", "/users/2", {"name": "Updated Name"}),
    ("PUT", "/categories/1", {"name": "Updated Category"}),
    ("DELETE", "/tasks/10", None),
    ("DELETE", "/users/3", None),
    ("DELETE", "/categories/4", None),
]


def free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def status_class(code):
    return f"{code // 100}xx"


def top_keys(body_text):
    """Loose top-level shape. dict -> sorted keys; list -> marker + first-elem keys."""
    try:
        data = json.loads(body_text)
    except Exception:
        return {"_type": "non-json"}
    if isinstance(data, dict):
        return {"_type": "dict", "keys": sorted(data.keys())}
    if isinstance(data, list):
        first = data[0] if data and isinstance(data[0], dict) else None
        return {"_type": "list", "first_keys": sorted(first.keys()) if first else []}
    return {"_type": type(data).__name__}


def init_db():
    # Self-initialize: create schema then seed. Independent of import side effects.
    with app.app_context():
        db.create_all()
    seed_data()  # uses model.set_password -> hash migration flows automatically


class ServerThread(threading.Thread):
    def __init__(self, port):
        super().__init__(daemon=True)
        self.srv = make_server("127.0.0.1", port, app)
        self.ctx = app.app_context()

    def run(self):
        self.srv.serve_forever()

    def stop(self):
        self.srv.shutdown()


def wait_ready(base):
    for _ in range(100):
        try:
            r = requests.get(base + "/health", timeout=1)
            if r.status_code < 500:
                return True
        except Exception:
            pass
        time.sleep(0.1)
    return False


def capture():
    init_db()
    port = free_port()
    server = ServerThread(port)
    server.start()
    base = f"http://127.0.0.1:{port}"
    if not wait_ready(base):
        raise RuntimeError("app did not become ready")

    records = []
    for method, path, body in ROUTES:
        kwargs = {"timeout": 5}
        if body is not None:
            kwargs["json"] = body  # requests sets Content-Type: application/json
        resp = requests.request(method, base + path, **kwargs)
        records.append({
            "method": method,
            "path": path,
            "status_code": resp.status_code,
            "status_class": status_class(resp.status_code),
            "top_keys": top_keys(resp.text),
        })
    server.stop()
    return records


def main():
    out_path = sys.argv[1]
    records = capture()
    with open(out_path, "w") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    fivexx = [r for r in records if r["status_class"] == "5xx"]
    print(f"Captured {len(records)} endpoints -> {out_path}")
    for r in records:
        flag = "  <-- 5xx!" if r["status_class"] == "5xx" else ""
        print(f"  {r['method']:6} {r['path']:28} {r['status_code']} ({r['status_class']}){flag}")
    if fivexx:
        print(f"\nWARNING: {len(fivexx)} endpoint(s) returned 5xx.")

    if "--compare" in sys.argv:
        baseline_path = sys.argv[sys.argv.index("--compare") + 1]
        with open(baseline_path) as f:
            baseline = json.load(f)
        compare(baseline, records)


def compare(baseline, current):
    bmap = {(r["method"], r["path"]): r for r in baseline}
    cmap = {(r["method"], r["path"]): r for r in current}
    status_regressions = []
    key_notes = []
    for key, b in bmap.items():
        c = cmap.get(key)
        if c is None:
            status_regressions.append(f"{key}: MISSING in current run")
            continue
        if b["status_class"] != c["status_class"]:
            status_regressions.append(
                f"{key[0]} {key[1]}: {b['status_class']} -> {c['status_class']}")
        # loose top-key diff (informational); tolerate removed sensitive fields
        bk = set(b["top_keys"].get("keys", b["top_keys"].get("first_keys", [])))
        ck = set(c["top_keys"].get("keys", c["top_keys"].get("first_keys", [])))
        removed = bk - ck
        if removed:
            tolerated = removed & SENSITIVE_FIELDS
            untolerated = removed - SENSITIVE_FIELDS
            key_notes.append(
                f"{key[0]} {key[1]}: removed top keys {sorted(removed)}"
                f" (sensitive-tolerated: {sorted(tolerated)}; other: {sorted(untolerated)})")

    print("\n=== HARNESS COMPARE ===")
    if status_regressions:
        print("STATUS-CLASS REGRESSIONS (RED):")
        for s in status_regressions:
            print("  " + s)
    else:
        print("GREEN: status class identical for all endpoints.")
    if key_notes:
        print("Top-key changes (informational, body shape is loose):")
        for n in key_notes:
            print("  " + n)
    print("RESULT:", "RED" if status_regressions else "GREEN")
    if status_regressions:
        sys.exit(1)


if __name__ == "__main__":
    main()
