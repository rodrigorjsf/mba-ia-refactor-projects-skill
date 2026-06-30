"""Composition root: build the app, load config, register routes + error
handler. No side effects at import time (schema creation is explicit)."""
from datetime import datetime

from flask import Flask
from flask_cors import CORS

from config import settings
from database import db
from middlewares.error_handler import register_error_handlers
from routes.task_routes import task_bp
from routes.user_routes import user_bp
from routes.report_routes import report_bp


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = settings.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = settings.SQLALCHEMY_TRACK_MODIFICATIONS
    app.config['SECRET_KEY'] = settings.SECRET_KEY
    app.config['DEBUG'] = settings.DEBUG

    CORS(app)
    db.init_app(app)

    app.register_blueprint(task_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(report_bp)

    @app.route('/health')
    def health():
        return {'status': 'ok', 'timestamp': str(datetime.now())}

    @app.route('/')
    def index():
        return {'message': 'Task Manager API', 'version': '1.0'}

    register_error_handlers(app)
    return app


def init_db(app):
    """Explicit schema creation (no I/O at import time)."""
    with app.app_context():
        db.create_all()


# Module-level app so `from app import app, db` keeps working (seed, harness).
app = create_app()


if __name__ == '__main__':
    init_db(app)
    app.run(debug=settings.DEBUG, host='0.0.0.0', port=5000)
