from __future__ import annotations

import os

import pytest

from app import create_app, db


@pytest.fixture()
def app(tmp_path):
    os.environ["FLASK_ENV"] = "development"
    os.environ["DATABASE_PATH"] = str(tmp_path / "test_monitor_system.db")
    os.environ["MONITORING_SCHEDULER_ENABLED"] = "false"

    flask_app = create_app("development")
    flask_app.config.update(TESTING=True, SECRET_KEY="test-secret")

    with flask_app.app_context():
        db.drop_all()
        db.create_all()

    yield flask_app

    with flask_app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()
