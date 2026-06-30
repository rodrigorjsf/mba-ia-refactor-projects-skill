"""Admin controller — destructive maintenance, now secured.

The original exposed two UNAUTHENTICATED admin endpoints (CRITICAL findings in
reports/audit-project-1.md):

  - POST /admin/query    — executed arbitrary SQL from the request body. There is
    no safe form of this, so it was REMOVED entirely. The route no longer exists;
    requests now get 404.
  - POST /admin/reset-db — wiped all tables with no authentication. It is kept,
    but now requires a valid `X-Admin-Token` header (matching the ADMIN_TOKEN
    env var). Without it the endpoint returns 401 and touches nothing.

These are INTENTIONAL security changes that alter the HTTP status class versus
the original (200 -> 404 / 401). The characterization baseline was re-baselined
accordingly (harness/baseline.json) and the change is documented in the audit
report — see references/mvc-guidelines.md › "exceção ao harness verde".
"""
import os

from flask import jsonify, request

from database.connection import get_db

ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN")


def _authorized():
    """True only when ADMIN_TOKEN is configured and the request presents it."""
    token = request.headers.get("X-Admin-Token")
    return bool(ADMIN_TOKEN) and token == ADMIN_TOKEN


def reset_db():
    if not _authorized():
        return jsonify({"erro": "Não autorizado"}), 401
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM itens_pedido")
    cursor.execute("DELETE FROM pedidos")
    cursor.execute("DELETE FROM produtos")
    cursor.execute("DELETE FROM usuarios")
    db.commit()
    return jsonify({"mensagem": "Banco de dados resetado", "sucesso": True}), 200
