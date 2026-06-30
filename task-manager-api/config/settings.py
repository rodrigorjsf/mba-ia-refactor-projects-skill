"""Application configuration read from the environment.

No real production secret is hardcoded. A clearly-marked dev-only default lets
the app boot with a single command; production must supply the real values via
environment variables.
"""
import os


def _as_bool(value, default=False):
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


# Secrets / config from the environment (dev-only defaults, replace in prod).
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-in-production")
DEBUG = _as_bool(os.environ.get("DEBUG"), default=False)

SQLALCHEMY_DATABASE_URI = os.environ.get(
    "DATABASE_URL", "sqlite:///tasks.db"
)
SQLALCHEMY_TRACK_MODIFICATIONS = False

# SMTP credentials for the notification service (no real secret in code).
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_USER = os.environ.get("EMAIL_USER", "taskmanager@example.com")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD", "")
