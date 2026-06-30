"""Centralized error handling.

A single place catches unhandled exceptions and returns a standardized 500
without leaking internal detail (no `str(e)` in the body). HTTP exceptions
raised by routing (404/405/...) keep their own status.
"""
from flask import jsonify
from werkzeug.exceptions import HTTPException


def register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_http_exception(exc):
        return jsonify({"erro": exc.name}), exc.code

    @app.errorhandler(Exception)
    def handle_unexpected(exc):
        app.logger.exception("Erro não tratado: %s", exc)
        return jsonify({"erro": "Erro interno"}), 500
