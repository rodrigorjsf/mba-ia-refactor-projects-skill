"""Notification side effects, isolated from the controllers.

In the original code the order/status handlers emitted e-mail/SMS/push directly
(as prints) inline. Here the effect lives in one stubbable service so the
controller only orchestrates and the effect is testable in isolation.
"""
import logging

logger = logging.getLogger("loja.notifications")


class NotificationService:
    def pedido_criado(self, pedido_id, usuario_id):
        logger.info(
            "Notificando pedido %s do usuario %s (email/sms/push)",
            pedido_id,
            usuario_id,
        )

    def status_alterado(self, pedido_id, novo_status):
        if novo_status == "aprovado":
            logger.info("Pedido %s aprovado — preparar envio", pedido_id)
        elif novo_status == "cancelado":
            logger.info("Pedido %s cancelado — devolver estoque", pedido_id)


notification_service = NotificationService()
