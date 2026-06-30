"""Produto controller — orchestrates validation, model calls and responses.

No SQL, no try/except str(e) (unhandled errors go to the central error
handler). Input validation is centralized in one helper shared by create and
update.
"""
from flask import jsonify, request

from models import produto_model


def _validar_produto(dados):
    """Return an error message string if invalid, else None."""
    if not dados:
        return "Dados inválidos"
    if "nome" not in dados:
        return "Nome é obrigatório"
    if "preco" not in dados:
        return "Preço é obrigatório"
    if "estoque" not in dados:
        return "Estoque é obrigatório"
    if dados["preco"] < 0:
        return "Preço não pode ser negativo"
    if dados["estoque"] < 0:
        return "Estoque não pode ser negativo"
    nome = dados["nome"]
    if len(nome) < 2:
        return "Nome muito curto"
    if len(nome) > 200:
        return "Nome muito longo"
    categoria = dados.get("categoria", "geral")
    if categoria not in produto_model.CATEGORIAS_VALIDAS:
        return "Categoria inválida. Válidas: " + str(produto_model.CATEGORIAS_VALIDAS)
    return None


def listar():
    return jsonify({"dados": produto_model.get_todos(), "sucesso": True}), 200


def buscar(id):
    produto = produto_model.get_por_id(id)
    if produto:
        return jsonify({"dados": produto, "sucesso": True}), 200
    return jsonify({"erro": "Produto não encontrado", "sucesso": False}), 404


def criar():
    dados = request.get_json(silent=True)
    erro = _validar_produto(dados)
    if erro:
        return jsonify({"erro": erro}), 400

    produto_id = produto_model.criar(
        dados["nome"],
        dados.get("descricao", ""),
        dados["preco"],
        dados["estoque"],
        dados.get("categoria", "geral"),
    )
    return jsonify({"dados": {"id": produto_id}, "sucesso": True, "mensagem": "Produto criado"}), 201


def atualizar(id):
    if not produto_model.get_por_id(id):
        return jsonify({"erro": "Produto não encontrado"}), 404

    dados = request.get_json(silent=True)
    erro = _validar_produto(dados)
    if erro:
        return jsonify({"erro": erro}), 400

    produto_model.atualizar(
        id,
        dados["nome"],
        dados.get("descricao", ""),
        dados["preco"],
        dados["estoque"],
        dados.get("categoria", "geral"),
    )
    return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200


def deletar(id):
    if not produto_model.get_por_id(id):
        return jsonify({"erro": "Produto não encontrado"}), 404
    produto_model.deletar(id)
    return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200


def busca():
    termo = request.args.get("q", "")
    categoria = request.args.get("categoria", None)
    preco_min = request.args.get("preco_min", None)
    preco_max = request.args.get("preco_max", None)
    if preco_min:
        preco_min = float(preco_min)
    if preco_max:
        preco_max = float(preco_max)

    resultados = produto_model.buscar(termo, categoria, preco_min, preco_max)
    return jsonify({"dados": resultados, "total": len(resultados), "sucesso": True}), 200
