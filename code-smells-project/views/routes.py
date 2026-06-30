"""HTTP route map: METHOD /path -> controller function.

No business logic here — just wiring. Paths and methods are identical to the
original monolith so the external contract (and the characterization harness)
is preserved.
"""
from controllers import (
    admin_controller,
    pedido_controller,
    produto_controller,
    relatorio_controller,
    system_controller,
    usuario_controller,
)


def register_routes(app):
    # System
    app.add_url_rule("/", "index", system_controller.index, methods=["GET"])
    app.add_url_rule("/health", "health_check", system_controller.health, methods=["GET"])

    # Produtos
    app.add_url_rule("/produtos", "listar_produtos", produto_controller.listar, methods=["GET"])
    app.add_url_rule("/produtos/busca", "buscar_produtos", produto_controller.busca, methods=["GET"])
    app.add_url_rule("/produtos/<int:id>", "buscar_produto", produto_controller.buscar, methods=["GET"])
    app.add_url_rule("/produtos", "criar_produto", produto_controller.criar, methods=["POST"])
    app.add_url_rule("/produtos/<int:id>", "atualizar_produto", produto_controller.atualizar, methods=["PUT"])
    app.add_url_rule("/produtos/<int:id>", "deletar_produto", produto_controller.deletar, methods=["DELETE"])

    # Usuários
    app.add_url_rule("/usuarios", "listar_usuarios", usuario_controller.listar, methods=["GET"])
    app.add_url_rule("/usuarios/<int:id>", "buscar_usuario", usuario_controller.buscar, methods=["GET"])
    app.add_url_rule("/usuarios", "criar_usuario", usuario_controller.criar, methods=["POST"])
    app.add_url_rule("/login", "login", usuario_controller.login, methods=["POST"])

    # Pedidos
    app.add_url_rule("/pedidos", "criar_pedido", pedido_controller.criar, methods=["POST"])
    app.add_url_rule("/pedidos", "listar_todos_pedidos", pedido_controller.listar_todos, methods=["GET"])
    app.add_url_rule("/pedidos/usuario/<int:usuario_id>", "listar_pedidos_usuario", pedido_controller.listar_usuario, methods=["GET"])
    app.add_url_rule("/pedidos/<int:pedido_id>/status", "atualizar_status_pedido", pedido_controller.atualizar_status, methods=["PUT"])

    # Relatórios
    app.add_url_rule("/relatorios/vendas", "relatorio_vendas", relatorio_controller.vendas, methods=["GET"])

    # Admin (destrutivo, agora protegido por auth — ver admin_controller / auditoria).
    # /admin/query (SQL arbitrário) foi REMOVIDO por segurança — sem rota -> 404.
    app.add_url_rule("/admin/reset-db", "reset_database", admin_controller.reset_db, methods=["POST"])
