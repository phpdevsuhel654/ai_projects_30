from __future__ import annotations

from app.routes import monitoring


def test_monitoring_api_crud_and_execution(client):
    add_response = client.post(
        "/api/v1/monitoring/urls",
        json={"url": "https://api.example.com", "notes": "api", "is_active": True},
    )
    assert add_response.status_code == 201
    created = add_response.get_json()
    url_id = created["id"]

    list_response = client.get("/api/v1/monitoring/urls")
    assert list_response.status_code == 200
    assert len(list_response.get_json()["items"]) == 1

    update_response = client.put(
        f"/api/v1/monitoring/urls/{url_id}",
        json={"url": "https://api2.example.com", "notes": "updated", "is_active": True},
    )
    assert update_response.status_code == 200
    assert update_response.get_json()["url"] == "https://api2.example.com"

    monitoring.service._check_single_url = lambda _url: {
        "dns_resolved": True,
        "http_status_code": 200,
        "https_valid": True,
        "response_time_ms": 25,
        "availability_status": "UP",
        "error_message": None,
    }

    execute_response = client.post("/api/v1/monitoring/execute", json={"initiated_by": "pytest"})
    assert execute_response.status_code == 200
    run_payload = execute_response.get_json()
    assert run_payload["total_urls"] == 1
    assert run_payload["overall_status"] == "SUCCESS"

    reports_response = client.get("/api/v1/monitoring/reports?limit=10")
    assert reports_response.status_code == 200
    items = reports_response.get_json()["items"]
    assert len(items) == 1

    detail_response = client.get(f"/api/v1/monitoring/reports/{items[0]['id']}")
    assert detail_response.status_code == 200
    assert len(detail_response.get_json()["execution_details"]) == 1

    delete_response = client.delete(f"/api/v1/monitoring/urls/{url_id}")
    assert delete_response.status_code == 200


def test_monitoring_api_validation_errors(client):
    bad_add = client.post("/api/v1/monitoring/urls", json={"url": "example.com"})
    assert bad_add.status_code == 400

    bad_limit = client.get("/api/v1/monitoring/reports?limit=abc")
    assert bad_limit.status_code == 400


def test_monitoring_scheduler_endpoints(client):
    status_response = client.get("/api/v1/monitoring/scheduler/status")
    assert status_response.status_code == 200
    status_payload = status_response.get_json()
    assert "configured" in status_payload
    assert "running" in status_payload
    assert "cron" in status_payload

    monitoring.monitoring_scheduler_service.run_now = lambda app, initiated_by: {
        "id": 999,
        "overall_status": "SUCCESS",
        "initiated_by": initiated_by,
        "total_urls": 0,
        "success_urls": 0,
        "failed_urls": 0,
        "execution_details": [],
    }

    run_response = client.post("/api/v1/monitoring/scheduler/run-now", json={"initiated_by": "pytest-scheduler"})
    assert run_response.status_code == 200
    run_payload = run_response.get_json()
    assert run_payload["overall_status"] == "SUCCESS"
    assert run_payload["initiated_by"] == "pytest-scheduler"
