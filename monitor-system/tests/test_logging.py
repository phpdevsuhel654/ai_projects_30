from __future__ import annotations


def test_request_id_added_when_missing(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.headers.get("X-Request-ID")


def test_request_id_preserved_when_provided(client):
    response = client.get("/health", headers={"X-Request-ID": "req-123"})
    assert response.status_code == 200
    assert response.headers.get("X-Request-ID") == "req-123"


def test_http_exception_not_overridden_by_generic_handler(client):
    response = client.get("/route-that-does-not-exist")
    assert response.status_code == 404
