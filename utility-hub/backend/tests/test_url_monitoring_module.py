from app.controllers import monitoring_controller


def test_monitoring_api_crud_and_execution(client):
    add_response = client.post(
        "/api/monitoring/urls",
        json={"url": "https://api.example.com", "notes": "api", "is_active": True},
    )
    assert add_response.status_code == 201
    created = add_response.get_json()
    url_id = created["id"]

    list_response = client.get("/api/monitoring/urls")
    assert list_response.status_code == 200
    assert len(list_response.get_json()["items"]) == 1

    update_response = client.put(
        f"/api/monitoring/urls/{url_id}",
        json={"url": "https://api2.example.com", "notes": "updated", "is_active": True},
    )
    assert update_response.status_code == 200
    assert update_response.get_json()["url"] == "https://api2.example.com"

    monitoring_controller.service._check_single_url = lambda _url: {
        "dns_resolved": True,
        "http_status_code": 200,
        "https_valid": True,
        "response_time_ms": 25,
        "availability_status": "UP",
        "error_message": None,
    }

    execute_response = client.post("/api/monitoring/execute", json={"initiated_by": "pytest"})
    assert execute_response.status_code == 200
    run_payload = execute_response.get_json()
    assert run_payload["total_urls"] == 1
    assert run_payload["overall_status"] == "SUCCESS"

    reports_response = client.get("/api/monitoring/reports?limit=10")
    assert reports_response.status_code == 200
    items = reports_response.get_json()["items"]
    assert len(items) == 1

    detail_response = client.get(f"/api/monitoring/reports/{items[0]['id']}")
    assert detail_response.status_code == 200
    assert len(detail_response.get_json()["execution_details"]) == 1

    delete_response = client.delete(f"/api/monitoring/urls/{url_id}")
    assert delete_response.status_code == 200


def test_monitoring_dashboard_loads(client):
    response = client.get("/url-monitoring")
    assert response.status_code == 200
    assert b"URL Monitoring" in response.data
