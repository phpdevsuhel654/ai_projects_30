import re

from app.extensions import db
from app.models.user import User


def _create_user(app, email="user@example.com", password="secret123"):
    with app.app_context():
        user = User(full_name="Normal User", email=email, role="student")
        user.set_password(password)
        db.session.add(user)
        db.session.commit()


def _login(client, email, password="secret123"):
    return client.post(
        "/auth/login",
        data={"email": email, "password": password},
        follow_redirects=True,
    )


def test_profile_update(app, client):
    _create_user(app)
    _login(client, "user@example.com")

    response = client.post(
        "/auth/profile",
        data={"full_name": "Updated User", "email": "updated@example.com"},
        follow_redirects=True,
    )

    assert response.status_code == 200

    with app.app_context():
        user = User.query.filter_by(email="updated@example.com").first()
        assert user is not None
        assert user.full_name == "Updated User"


def test_password_reset_flow(app, client):
    _create_user(app, email="reset@example.com")

    response = client.post(
        "/auth/forgot-password",
        data={"email": "reset@example.com"},
        follow_redirects=True,
    )
    assert response.status_code == 200

    html = response.get_data(as_text=True)
    match = re.search(r"/auth/reset-password/[^\"\s<]+", html)
    assert match is not None

    reset_path = match.group(0)

    response = client.post(
        reset_path,
        data={"password": "new-secret123"},
        follow_redirects=True,
    )
    assert response.status_code == 200

    client.get("/auth/logout", follow_redirects=True)
    login_response = _login(client, "reset@example.com", password="new-secret123")
    assert b"Logged in successfully" in login_response.data


def test_user_chat_history_page(app, client):
    _create_user(app, email="history@example.com")
    _login(client, "history@example.com")

    chat_response = client.post(
        "/api/chat",
        json={"message": "Tell me about hostel", "session_id": "history-session"},
    )
    assert chat_response.status_code == 200

    history_response = client.get("/auth/history")
    assert history_response.status_code == 200
    assert b"Tell me about hostel" in history_response.data
