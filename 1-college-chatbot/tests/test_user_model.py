from app.extensions import db
from app.models.user import User


def test_password_hash_and_verify(app):
    with app.app_context():
        user = User(full_name="Test User", email="test@example.com")
        user.set_password("secret123")

        db.session.add(user)
        db.session.commit()

        assert user.password_hash != "secret123"
        assert user.check_password("secret123") is True
        assert user.check_password("wrong") is False
