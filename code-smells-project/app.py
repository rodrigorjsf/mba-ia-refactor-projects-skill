"""Composition root for the Loja API.

Builds the Flask app explicitly: loads config from the environment, wires the
per-request DB connection, registers routes and the centralized error handler,
and initializes the schema/seed. No side effect at import time other than this
explicit wiring; nothing here talks to HTTP request/response or SQL directly.

Run:
    python app.py            # honors SECRET_KEY / DEBUG / PORT / DB_PATH env vars
"""
from flask import Flask
from flask_cors import CORS

from config import settings
from database.connection import init_db, register_db
from middlewares.error_handler import register_error_handlers
from views.routes import register_routes


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    app.config["DEBUG"] = settings.DEBUG
    CORS(app)

    register_db(app)
    register_routes(app)
    register_error_handlers(app)

    init_db()
    return app


app = create_app()


if __name__ == "__main__":
    print("=" * 50)
    print("SERVIDOR INICIADO")
    print(f"Rodando em http://{settings.HOST}:{settings.PORT}")
    print("=" * 50)
    app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
