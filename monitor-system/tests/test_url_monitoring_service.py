from __future__ import annotations

from app.services.url_health_check_service import URLHealthCheckService


def test_url_service_crud_flow(app):
    service = URLHealthCheckService()

    created = service.add_url({"url": "https://example.com", "notes": "main", "is_active": True})
    assert created["id"] > 0
    assert created["url"] == "https://example.com"

    listed = service.list_urls(active_only=False)
    assert len(listed) == 1

    updated = service.update_url(created["id"], {"url": "https://example.org", "notes": "updated", "is_active": False})
    assert updated["url"] == "https://example.org"
    assert updated["is_active"] is False

    deleted = service.delete_url(created["id"])
    assert deleted is True
    assert service.list_urls(active_only=False) == []


def test_url_service_execute_checks_and_report(app):
    service = URLHealthCheckService()
    service.add_url({"url": "https://up.example", "is_active": True})
    service.add_url({"url": "https://down.example", "is_active": True})

    def fake_check(url: str):
        if "up.example" in url:
            return {
                "dns_resolved": True,
                "http_status_code": 200,
                "https_valid": True,
                "response_time_ms": 42,
                "availability_status": "UP",
                "error_message": None,
            }
        return {
            "dns_resolved": True,
            "http_status_code": 503,
            "https_valid": True,
            "response_time_ms": 88,
            "availability_status": "DOWN",
            "error_message": "Service unavailable",
        }

    service._check_single_url = fake_check  # noqa: SLF001

    run_result = service.execute_checks(trigger_type="MANUAL", initiated_by="pytest")
    assert run_result["total_urls"] == 2
    assert run_result["success_urls"] == 1
    assert run_result["failed_urls"] == 1
    assert run_result["overall_status"] == "PARTIAL"
    assert len(run_result["execution_details"]) == 2

    history = service.list_history(limit=5)
    assert len(history) == 1
    report = service.get_report(history[0]["id"])
    assert report["id"] == history[0]["id"]
    assert len(report["execution_details"]) == 2
