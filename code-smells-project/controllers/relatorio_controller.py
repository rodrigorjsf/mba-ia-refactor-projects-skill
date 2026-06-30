"""Relatório controller — exposes the sales report."""
from flask import jsonify

from models import relatorio_model


def vendas():
    return jsonify({"dados": relatorio_model.gerar(), "sucesso": True}), 200
