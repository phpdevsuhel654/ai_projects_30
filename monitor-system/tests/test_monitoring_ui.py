from __future__ import annotations

from app.routes import monitoring_ui


def test_monitoring_dashboard_page_loads(client):
    response = client.get("/url-monitoring")
    assert response.status_code == 200
    assert b"URL Monitoring" in response.data
    assert b"Scheduler" in response.data


def test_monitoring_ui_add_and_execute(client):
    add_response = client.post(
        "/url-monitoring/add",
        data={"url": "https://ui.example.com", "notes": "ui", "is_active": "on"},
        follow_redirects=True,
    )
    assert add_response.status_code == 200
    assert b"URL added successfully" in add_response.data

    monitoring_ui.service._check_single_url = lambda _url: {
        "dns_resolved": True,
        "http_status_code": 200,
        "https_valid": True,
        "response_time_ms": 33,
        "availability_status": "UP",
        "error_message": None,
    }

    run_response = client.post(
        "/url-monitoring/execute",
        data={"initiated_by": "pytest-ui"},
        follow_redirects=True,
    )
    assert run_response.status_code == 200
    assert b"Health check execution completed" in run_response.data
    assert b"ui.example.com" in run_response.data
