import pytest

from app import create_app
from app.chatbot.seed_data import seed_phase1_knowledge_base
from app.extensions import db


@pytest.fixture
def app():
    app = create_app(
        "testing",
        {
            "TESTING": True,
            "WTF_CSRF_ENABLED": False,
            "SECRET_KEY": "test-secret",
            "API_CHAT_RATE_LIMIT": "100 per minute",
        },
    )

    with app.app_context():
        db.create_all()
        seed_phase1_knowledge_base()

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()
