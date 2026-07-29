from flask import Flask

from sqlalchemy import text

from app.config.logging import configure_logging
from app.config.settings import Config
from app.controllers.address_controller import address_bp
from app.controllers.address_web_controller import address_web_bp
from app.controllers.health_controller import health_bp
from app.controllers.cron_controller import cron_bp
from app.controllers.execution_controller import execution_bp
from app.controllers.monitoring_controller import monitoring_bp
from app.controllers.monitoring_web_controller import monitoring_web_bp
from app.controllers.web_controller import web_bp
from app.models import (
    AddressValidation,
    CronJob,
    ExecutionDetail,
    ExecutionHistory,
    ExecutionLog,
    ExecutionLogArchive,
    MonitoredURL,
)
from app.scheduler.job_scheduler import job_scheduler
from app.services.monitoring_scheduler_service import monitoring_scheduler_service
from app.utils.extensions import db, migrate
from app.utils.security import register_security_headers


def _ensure_sqlite_compatibility_migrations(app: Flask) -> None:
    db_uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
    if not db_uri.startswith("sqlite"):
        return

    # Keep local/dev databases compatible after incremental schema changes.
    with db.engine.begin() as conn:
        table_rows = conn.execute(text("PRAGMA table_info(execution_logs)")).fetchall()
        existing_columns = {row[1] for row in table_rows}

        if "bulk_execution_id" not in existing_columns:
            conn.execute(text("ALTER TABLE execution_logs ADD COLUMN bulk_execution_id VARCHAR(64)"))

        conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS idx_execution_logs_bulk_execution_id "
                "ON execution_logs(bulk_execution_id)"
            )
        )


def create_app(config_overrides: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    if config_overrides:
        app.config.update(config_overrides)

    configure_logging(app)
    register_security_headers(app)

    db.init_app(app)
    migrate.init_app(app, db, directory="database/migrations")

    app.register_blueprint(health_bp)
    app.register_blueprint(web_bp)
    app.register_blueprint(address_web_bp)
    app.register_blueprint(monitoring_web_bp)
    app.register_blueprint(cron_bp, url_prefix="/api")
    app.register_blueprint(execution_bp, url_prefix="/api")
    app.register_blueprint(address_bp)
    app.register_blueprint(monitoring_bp)

    with app.app_context():
        _ = (
            CronJob,
            ExecutionLog,
            ExecutionLogArchive,
            AddressValidation,
            MonitoredURL,
            ExecutionHistory,
            ExecutionDetail,
        )
        db.create_all()
        _ensure_sqlite_compatibility_migrations(app)

    if app.config.get("SCHEDULER_ENABLED", True):
        job_scheduler.start(app)

    monitoring_scheduler_service.start(app)

    return app
