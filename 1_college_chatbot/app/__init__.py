import os
from uuid import uuid4

from flask import Flask, g, request

from app.config import get_config
from app.extensions import bcrypt, db, limiter, login_manager
from app.models import ChatHistory, FAQCategory, KnowledgeBase, StudentQuery, User  # noqa: F401
from app.utils.logging_config import configure_logging


def create_app(config_name=None, config_overrides=None):
    app = Flask(__name__, template_folder="templates", static_folder="static")

    selected_config = config_name or os.getenv("APP_ENV", "development")
    app.config.from_object(get_config(selected_config))

    if config_overrides:
        app.config.update(config_overrides)

    _init_extensions(app)
    _init_logging(app)
    _register_request_hooks(app)
    _register_blueprints(app)

    with app.app_context():
        if app.config.get("AUTO_CREATE_TABLES", False):
            db.create_all()
            from app.chatbot.seed_data import seed_phase1_knowledge_base

            seed_phase1_knowledge_base()

    return app


def _init_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    limiter.init_app(app)


def _init_logging(app):
    configure_logging(app)


def _register_request_hooks(app):
    @app.before_request
    def _assign_request_id():
        g.request_id = request.headers.get("X-Request-ID", str(uuid4()))

    @app.after_request
    def _log_request(response):
        app.logger.info(
            "request_completed",
            extra={
                "request_id": getattr(g, "request_id", "-"),
                "method": request.method,
                "path": request.path,
                "status": response.status_code,
                "remote_addr": request.remote_addr or "-",
            },
        )
        response.headers["X-Request-ID"] = getattr(g, "request_id", "-")
        return response


def _register_blueprints(app):
    from app.admin import admin_bp
    from app.auth import auth_bp
    from app.chatbot import chatbot_bp
    from app.routes import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(chatbot_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")


@login_manager.user_loader
def _load_user(user_id):
    return db.session.get(User, int(user_id))
