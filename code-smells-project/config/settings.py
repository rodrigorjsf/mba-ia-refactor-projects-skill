"""Application configuration, read from the environment.

No secret is hardcoded here: every sensitive value comes from `os.environ`
with a safe, clearly dev-only default. In production, set SECRET_KEY/DEBUG
via the environment.
"""
import os

# Secret used by Flask for signing. The default is obviously a dev placeholder
# and must be overridden in production via the SECRET_KEY env var.
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-insecure-key-change-me")

# Debug is OFF by default and only enabled when DEBUG=true in the environment.
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"

# SQLite database file path.
DB_PATH = os.environ.get("DB_PATH", "loja.db")

# Bind host/port for the dev server.
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "5000"))
