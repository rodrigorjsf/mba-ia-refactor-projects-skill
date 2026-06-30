"""Pedido model — parametrized SQL, N+1 fixed, listing logic deduplicated.

Order assembly (`get_todos` / `get_por_usuario`) shares one helper that loads
every order's items in a single JOIN query instead of a query per item.
"""
from collections import defaultdict

from database.connection import get_db

STATUS_VALIDOS = ["pendente", "aprovado", "enviado", "entregue", "cancelado"]


def criar(usuario_id, itens):
    """Create an order: validate stock, compute total, persist, decrement stock.

    Returns {"pedido_id", "total"} on success, or {"erro": ...} on a business
    failure (unknown product / insufficient stock).
    """
    db = get_db()
    cursor = db.cursor()

    total = 0
    for item in itens:
        cursor.execute("SELECT * FROM produtos WHERE id = ?", (item["produto_id"],))
        produto = cursor.fetchone()
        if produto is None:
            return {"erro": "Produto " + str(item["produto_id"]) + " não encontrado"}
        if produto["estoque"] < item["quantidade"]:
            return {"erro": "Estoque insuficiente para " + produto["nome"]}
        total += produto["preco"] * item["quantidade"]

    cursor.execute(
        "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
        (usuario_id, total),
    )
    pedido_id = cursor.lastrowid

    for item in itens:
        cursor.execute("SELECT preco FROM produtos WHERE id = ?", (item["produto_id"],))
        produto = cursor.fetchone()
        cursor.execute(
            "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
            (pedido_id, item["produto_id"], item["quantidade"], produto["preco"]),
        )
        cursor.execute(
            "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
            (item["quantidade"], item["produto_id"]),
        )

    db.commit()
    return {"pedido_id": pedido_id, "total": total}


def _montar_pedidos(rows):
    """Build full order dicts (with items) using one query for all items."""
    if not rows:
        return []

    pedido_ids = [row["id"] for row in rows]
    placeholders = ",".join("?" * len(pedido_ids))
    cursor = get_db().cursor()
    cursor.execute(
        f"""
        SELECT ip.pedido_id, ip.produto_id, ip.quantidade, ip.preco_unitario,
               p.nome AS produto_nome
        FROM itens_pedido ip
        LEFT JOIN produtos p ON p.id = ip.produto_id
        WHERE ip.pedido_id IN ({placeholders})
        """,
        pedido_ids,
    )

    itens_por_pedido = defaultdict(list)
    for item in cursor.fetchall():
        itens_por_pedido[item["pedido_id"]].append({
            "produto_id": item["produto_id"],
            "produto_nome": item["produto_nome"] if item["produto_nome"] else "Desconhecido",
            "quantidade": item["quantidade"],
            "preco_unitario": item["preco_unitario"],
        })

    return [
        {
            "id": row["id"],
            "usuario_id": row["usuario_id"],
            "status": row["status"],
            "total": row["total"],
            "criado_em": row["criado_em"],
            "itens": itens_por_pedido.get(row["id"], []),
        }
        for row in rows
    ]


def get_todos():
    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM pedidos")
    return _montar_pedidos(cursor.fetchall())


def get_por_usuario(usuario_id):
    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM pedidos WHERE usuario_id = ?", (usuario_id,))
    return _montar_pedidos(cursor.fetchall())


def atualizar_status(pedido_id, novo_status):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE pedidos SET status = ? WHERE id = ?", (novo_status, pedido_id))
    db.commit()
    return True


def contar():
    cursor = get_db().cursor()
    cursor.execute("SELECT COUNT(*) FROM pedidos")
    return cursor.fetchone()[0]
