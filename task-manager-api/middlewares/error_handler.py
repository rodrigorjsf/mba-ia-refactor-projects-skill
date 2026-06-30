"""Centralized error handling: one place formats unexpected errors.

Handlers no longer repeat try/except -> str(e); internal detail never leaks.
"""
from flask import jsonify
from werkzeug.exceptions import HTTPException


def register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_http_exception(exc):
        # Preserve framework HTTP errors (404 for unknown routes, 405, etc.).
        return jsonify({'error': exc.description}), exc.code

    @app.errorhandler(Exception)
    def handle_unexpected(exc):
        app.logger.exception(exc)
        return jsonify({'error': 'Erro interno'}), 500
