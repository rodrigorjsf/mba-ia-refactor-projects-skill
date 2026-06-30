"""Relatório model — sales aggregation with named discount tiers.

The discount thresholds/rates are named constants instead of inline magic
numbers.
"""
from database.connection import get_db

# (faturamento mínimo, taxa de desconto) — avaliado da faixa mais alta p/ a mais baixa.
FAIXAS_DESCONTO = [
    (10000, 0.10),
    (5000, 0.05),
    (1000, 0.02),
]


def _calcular_desconto(faturamento):
    for minimo, taxa in FAIXAS_DESCONTO:
        if faturamento > minimo:
            return faturamento * taxa
    return 0


def gerar():
    cursor = get_db().cursor()

    cursor.execute("SELECT COUNT(*) FROM pedidos")
    total_pedidos = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(total) FROM pedidos")
    faturamento = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = ?", ("pendente",))
    pendentes = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = ?", ("aprovado",))
    aprovados = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = ?", ("cancelado",))
    cancelados = cursor.fetchone()[0]

    desconto = _calcular_desconto(faturamento)

    return {
        "total_pedidos": total_pedidos,
        "faturamento_bruto": round(faturamento, 2),
        "desconto_aplicavel": round(desconto, 2),
        "faturamento_liquido": round(faturamento - desconto, 2),
        "pedidos_pendentes": pendentes,
        "pedidos_aprovados": aprovados,
        "pedidos_cancelados": cancelados,
        "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0,
    }
