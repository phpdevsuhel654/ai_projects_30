from app.services.notification_service import NotificationService


class _Response:
    def __init__(self, status_code=200, text="ok"):
        self.status_code = status_code
        self.text = text


def test_api_auth_enforcement(app, client):
    app.config["API_AUTH_ENABLED"] = True
    app.config["API_AUTH_KEY"] = "test-key"

    unauthorized = client.get("/api/cron")
    assert unauthorized.status_code == 401

    authorized = client.get("/api/cron", headers={"X-API-Key": "test-key"})
    assert authorized.status_code == 200


def test_web_auth_redirect_and_login(app, client):
    app.config["WEB_AUTH_ENABLED"] = True
    app.config["WEB_AUTH_USERNAME"] = "admin"
    app.config["WEB_AUTH_PASSWORD"] = "secret"

    protected = client.get("/dashboard")
    assert protected.status_code == 302
    assert "/login" in protected.location

    login_response = client.post(
        "/login",
        data={"username": "admin", "password": "secret"},
        follow_redirects=True,
    )
    assert login_response.status_code == 200
    assert b"Execution Dashboard" in login_response.data


def test_security_headers_present(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("Referrer-Policy") == "no-referrer"
    assert response.headers.get("Permissions-Policy") is not None
    assert response.headers.get("Content-Security-Policy") is not None


def test_notification_triggered_on_run_job(app, client, monkeypatch):
    captured_payloads = []

    def capture(payload):
        captured_payloads.append(payload)

    monkeypatch.setattr("app.services.notification_service.NotificationService._send_payload", capture)
    monkeypatch.setattr("app.services.execution_service.requests.get", lambda *_args, **_kwargs: _Response())

    app.config["NOTIFICATIONS_ENABLED"] = True
    app.config["NOTIFY_ON_FAILURE"] = True
    app.config["NOTIFY_ON_SUMMARY"] = True

    create_response = client.post(
        "/api/cron",
        json={
            "name": "Notify Cron",
            "url": "https://example.com/cron",
            "execution_count": 1,
            "schedule_type": "daily",
        },
    )
    cron_id = create_response.get_json()["id"]

    run_response = client.post(f"/api/run/{cron_id}")
    assert run_response.status_code == 200
    assert len(captured_payloads) >= 1
    assert captured_payloads[0]["type"] == "cron_job_execution"


def test_notification_triggered_on_run_all_summary(app, client, monkeypatch):
    captured_payloads = []

    def capture(payload):
        captured_payloads.append(payload)

    monkeypatch.setattr("app.services.notification_service.NotificationService._send_payload", capture)
    monkeypatch.setattr("app.services.execution_service.requests.get", lambda *_args, **_kwargs: _Response())

    app.config["NOTIFICATIONS_ENABLED"] = True
    app.config["NOTIFY_ON_SUMMARY"] = True

    client.post(
        "/api/cron",
        json={
            "name": "Notify All Cron",
            "url": "https://example.com/cron",
            "execution_count": 1,
            "schedule_type": "daily",
        },
    )

    response = client.post("/api/run-all")
    assert response.status_code == 200
    assert any(item.get("type") == "run_all_summary" for item in captured_payloads)
