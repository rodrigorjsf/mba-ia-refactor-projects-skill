"""System controller — index and health check.

The health response no longer leaks secret_key/debug/db_path/internal config;
it reports only liveness and record counts.
"""
from flask import jsonify

from models import pedido_model, produto_model, usuario_model


def index():
    return jsonify({
        "mensagem": "Bem-vindo à API da Loja",
        "versao": "1.0.0",
        "endpoints": {
            "produtos": "/produtos",
            "usuarios": "/usuarios",
            "pedidos": "/pedidos",
            "login": "/login",
            "relatorios": "/relatorios/vendas",
            "health": "/health",
        },
    })


def health():
    return jsonify({
        "status": "ok",
        "database": "connected",
        "counts": {
            "produtos": produto_model.contar(),
            "usuarios": usuario_model.contar(),
            "pedidos": pedido_model.contar(),
        },
        "versao": "1.0.0",
    }), 200
