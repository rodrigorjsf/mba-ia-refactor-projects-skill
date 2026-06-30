from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def commit():
    """Commit the session; on failure roll back and re-raise so the centralized
    error handler returns a standardized 500 (no internal detail leaked)."""
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
