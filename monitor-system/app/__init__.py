from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from app.config.logging_config import register_request_logging, setup_logging
from app.config.settings import get_config


db = SQLAlchemy()
migrate = Migrate()


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(get_config(config_name))

    setup_logging(app)
    register_request_logging(app)

    db.init_app(app)

    from app import models  # noqa: F401

    if app.config.get("AUTO_CREATE_DB_ON_START", True):
        with app.app_context():
            db.create_all()
            app.logger.info("db_auto_create_all_completed")

    migrate.init_app(app, db)

    from app.routes.health import health_bp
    from app.routes.address import address_bp
    from app.routes.address_ui import address_ui_bp
    from app.routes.monitoring import monitoring_bp
    from app.routes.monitoring_ui import monitoring_ui_bp
    from app.routes.backup_ui import backup_ui_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(address_bp)
    app.register_blueprint(address_ui_bp)
    app.register_blueprint(monitoring_bp)
    app.register_blueprint(monitoring_ui_bp)
    app.register_blueprint(backup_ui_bp)

    from app.services.monitoring_scheduler_service import monitoring_scheduler_service

    monitoring_scheduler_service.start(app)

    app.logger.info("application_started env=%s", app.config.get("FLASK_ENV", "development"))

    return app
