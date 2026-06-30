"""Characterization harness for the Loja API (refactor-arch Phase 1 / Phase 3).

Boots the Flask app as a real HTTP server on a free port (cold subprocess
boot), hits every endpoint in the route map with a minimal valid payload, and
records {method, path, status_class, top_level_keys} per endpoint.

Usage:
    # capture baseline (before refactor)
    python harness/characterize.py --out harness/baseline.json

    # verify after refactor against the baseline (GREEN/RED gate)
    python harness/characterize.py --out harness/post.json --baseline harness/baseline.json

The app is imported as a WSGI object (`<module>:app`) and served via
`app.run(...)` on a free port, so the harness is port-agnostic and works for
both the original monolith and the refactored composition root (both expose an
importable `app`). The SQLite DB file is deleted before boot for a deterministic
fresh seed.
"""
import argparse
import json
import os
import socket
import subprocess
import sys
import time

import requests

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FILE = os.path.join(PROJECT_ROOT, "loja.db")

# Ordered request list. Order is deliberate so that every endpoint returns its
# natural success status class against a freshly seeded DB:
#   - reads first, then creates, then the records that depend on them,
#   - the destructive /admin/reset-db runs LAST (it wipes all tables).
# Each entry: (label, method, path, json_body_or_None)
REQUESTS = [
    ("index",                 "GET",    "/",                          None),
    ("health",                "GET",    "/health",                    None),
    ("listar_produtos",       "GET",    "/produtos",                  None),
    ("buscar_produtos",       "GET",    "/produtos/busca?q=note",     None),
    ("buscar_produto",        "GET",    "/produtos/1",                None),
    ("listar_usuarios",       "GET",    "/usuarios",                  None),
    ("buscar_usuario",        "GET",    "/usuarios/1",                None),
    ("criar_usuario",         "POST",   "/usuarios",                  {"nome": "Teste Harness", "email": "harness@loja.com", "senha": "segredo123"}),
    ("login",                 "POST",   "/login",                     {"email": "admin@loja.com", "senha": "admin123"}),
    ("criar_produto",         "POST",   "/produtos",                  {"nome": "Produto Harness", "preco": 10.0, "estoque": 5, "categoria": "geral"}),
    ("atualizar_produto",     "PUT",    "/produtos/1",                {"nome": "Notebook Atualizado", "preco": 5500.0, "estoque": 9, "categoria": "informatica"}),
    ("criar_pedido",          "POST",   "/pedidos",                   {"usuario_id": 1, "itens": [{"produto_id": 2, "quantidade": 1}]}),
    ("listar_todos_pedidos",  "GET",    "/pedidos",                   None),
    ("listar_pedidos_usuario","GET",    "/pedidos/usuario/1",         None),
    ("atualizar_status",      "PUT",    "/pedidos/1/status",          {"status": "aprovado"}),
    ("relatorio_vendas",      "GET",    "/relatorios/vendas",         None),
    ("deletar_produto",       "DELETE", "/produtos/10",               None),
    ("admin_query",           "POST",   "/admin/query",               {"sql": "SELECT 1"}),
    ("admin_reset_db",        "POST",   "/admin/reset-db",            None),
]


def pick_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def boot(module, port):
    runner = (
        "import os;"
        f"from {module} import app;"
        "app.run(host='127.0.0.1', port=int(os.environ['HARNESS_PORT']),"
        " debug=False, use_reloader=False)"
    )
    env = dict(os.environ)
    env["HARNESS_PORT"] = str(port)
    env["PORT"] = str(port)
    env["DB_PATH"] = DB_FILE
    return subprocess.Popen(
        [sys.executable, "-c", runner],
        cwd=PROJECT_ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


def wait_ready(base, proc, timeout=20.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if proc.poll() is not None:
            out = proc.stdout.read().decode("utf-8", "replace")
            raise RuntimeError("server process exited early:\n" + out)
        try:
            r = requests.get(base + "/", timeout=1.0)
            if r.status_code < 500:
                return
        except requests.RequestException:
            pass
        time.sleep(0.2)
    raise RuntimeError("server did not become ready in time")


def status_class(code):
    return f"{code // 100}xx"


def top_level_keys(resp):
    try:
        body = resp.json()
    except ValueError:
        return ["<non-json>"]
    if isinstance(body, dict):
        return sorted(body.keys())
    return [f"<{type(body).__name__}>"]


def run_requests(base):
    records = []
    for label, method, path, body in REQUESTS:
        url = base + path
        if method == "GET":
            r = requests.get(url, timeout=5)
        elif method == "DELETE":
            r = requests.delete(url, timeout=5)
        elif method == "POST":
            r = requests.post(url, json=(body or {}), timeout=5)
        elif method == "PUT":
            r = requests.put(url, json=(body or {}), timeout=5)
        else:
            raise ValueError("unsupported method " + method)
        # normalize path: strip query string for the route-map key
        clean_path = path.split("?", 1)[0]
        records.append({
            "label": label,
            "method": method,
            "path": clean_path,
            "status": r.status_code,
            "status_class": status_class(r.status_code),
            "top_level_keys": top_level_keys(r),
        })
    return records


def capture(module):
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    port = pick_free_port()
    base = f"http://127.0.0.1:{port}"
    proc = boot(module, port)
    try:
        wait_ready(base, proc)
        return run_requests(base)
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


def compare(baseline, current):
    """GREEN iff every endpoint's status_class matches the baseline.

    Body shape compared loosely (top-level keys); removed keys are tolerated
    (sensitive-field stripping), only status-class regressions are RED.
    """
    base_by_key = {(r["method"], r["path"]): r for r in baseline}
    red = []
    shape_changes = []
    for cur in current:
        key = (cur["method"], cur["path"])
        b = base_by_key.get(key)
        if b is None:
            red.append((key, "missing in baseline", None, cur["status_class"]))
            continue
        if b["status_class"] != cur["status_class"]:
            red.append((key, "status-class regression", b["status_class"], cur["status_class"]))
        removed = sorted(set(b["top_level_keys"]) - set(cur["top_level_keys"]))
        added = sorted(set(cur["top_level_keys"]) - set(b["top_level_keys"]))
        if removed or added:
            shape_changes.append((key, removed, added))
    return red, shape_changes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--module", default="app", help="import path exposing `app`")
    ap.add_argument("--out", required=True, help="where to write the capture JSON")
    ap.add_argument("--baseline", default=None, help="baseline JSON to compare against")
    args = ap.parse_args()

    records = capture(args.module)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    n5xx = [r for r in records if r["status_class"] == "5xx"]
    print(f"captured {len(records)} endpoints -> {args.out}")
    for r in records:
        print(f"  {r['status_class']}  {r['method']:6} {r['path']:32} keys={r['top_level_keys']}")
    if n5xx:
        print(f"WARNING: {len(n5xx)} unexpected 5xx in capture")

    if args.baseline:
        with open(args.baseline, encoding="utf-8") as f:
            baseline = json.load(f)
        red, shape_changes = compare(baseline, records)
        print("\n--- COMPARE vs baseline ---")
        if shape_changes:
            print("Tolerated shape changes (top-level keys):")
            for key, removed, added in shape_changes:
                print(f"  {key[0]} {key[1]}: removed={removed} added={added}")
        if red:
            print("RED — status-class regressions:")
            for key, why, b, c in red:
                print(f"  {key[0]} {key[1]}: {why} (baseline={b} current={c})")
            sys.exit(1)
        print("GREEN — every endpoint preserved its status class.")
        return 0


if __name__ == "__main__":
    main()
