"""Pedido controller — orchestrates order creation/listing/status changes.

Business rules live in the model; the external notification effect lives in the
notification service. The controller only validates input and wires them.
"""
from flask import jsonify, request

from models import pedido_model
from services.notification_service import notification_service


def criar():
    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({"erro": "Dados inválidos"}), 400

    usuario_id = dados.get("usuario_id")
    itens = dados.get("itens", [])

    if not usuario_id:
        return jsonify({"erro": "Usuario ID é obrigatório"}), 400
    if not itens or len(itens) == 0:
        return jsonify({"erro": "Pedido deve ter pelo menos 1 item"}), 400

    resultado = pedido_model.criar(usuario_id, itens)
    if "erro" in resultado:
        return jsonify({"erro": resultado["erro"], "sucesso": False}), 400

    notification_service.pedido_criado(resultado["pedido_id"], usuario_id)
    return jsonify({"dados": resultado, "sucesso": True, "mensagem": "Pedido criado com sucesso"}), 201


def listar_usuario(usuario_id):
    return jsonify({"dados": pedido_model.get_por_usuario(usuario_id), "sucesso": True}), 200


def listar_todos():
    return jsonify({"dados": pedido_model.get_todos(), "sucesso": True}), 200


def atualizar_status(pedido_id):
    dados = request.get_json(silent=True) or {}
    novo_status = dados.get("status", "")

    if novo_status not in pedido_model.STATUS_VALIDOS:
        return jsonify({"erro": "Status inválido"}), 400

    pedido_model.atualizar_status(pedido_id, novo_status)
    notification_service.status_alterado(pedido_id, novo_status)
    return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200
