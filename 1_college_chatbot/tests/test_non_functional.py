def test_api_docs_page(client):
    response = client.get("/api/docs")
    assert response.status_code == 200
    assert b"API Documentation" in response.data


def test_openapi_json_endpoint(client):
    response = client.get("/api/openapi.json")
    assert response.status_code == 200

    data = response.get_json()
    assert data["openapi"] == "3.0.3"
    assert "/api/chat" in data["paths"]


def test_request_id_header_present(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers.get("X-Request-ID")


def test_chat_api_rate_limit(client, app):
    app.config["API_CHAT_RATE_LIMIT"] = "2 per minute"

    payload = {"message": "hostel info", "session_id": "limit-test"}
    overrides = {"REMOTE_ADDR": "10.20.30.40"}

    first = client.post("/api/chat", json=payload, environ_overrides=overrides)
    second = client.post("/api/chat", json=payload, environ_overrides=overrides)
    third = client.post("/api/chat", json=payload, environ_overrides=overrides)

    assert first.status_code == 200
    assert second.status_code == 200
    assert third.status_code == 429
