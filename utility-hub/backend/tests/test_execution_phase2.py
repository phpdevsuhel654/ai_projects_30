import requests

from app.models import CronJob
from app.services.execution_service import ExecutionService
from app.utils.extensions import db


class _Response:
    def __init__(self, status_code: int, text: str = ""):
        self.status_code = status_code
        self.text = text


def _create_job() -> CronJob:
    job = CronJob(
        name="Retry Test",
        url="https://example.com/cron",
        execution_count=1,
        schedule_type="daily",
        is_active=True,
    )
    db.session.add(job)
    db.session.commit()
    return job


def test_retry_with_backoff_success_after_failures(app, monkeypatch):
    attempts = {"count": 0}

    def fake_get(url, timeout):
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise requests.RequestException("temporary network issue")
        return _Response(200, "ok")

    monkeypatch.setattr("app.services.execution_service.requests.get", fake_get)
    monkeypatch.setattr("app.services.execution_service.time.sleep", lambda _: None)

    with app.app_context():
        job = _create_job()
        result = ExecutionService.run_job(job.id)

    assert "error" not in result
    assert attempts["count"] == 3
    assert len(result["executions"]) == 1
    assert result["executions"][0]["status"] == "success"


def test_prevent_overlapping_execution(app, monkeypatch):
    monkeypatch.setattr(
        "app.services.execution_service.ExecutionService.execute_single_run",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("should not run")),
    )

    with app.app_context():
        job = _create_job()
        acquired = ExecutionService._try_acquire_job_lock(job.id)
        assert acquired is True

        try:
            result = ExecutionService.run_job(job.id)
        finally:
            ExecutionService._release_job_lock(job.id)

    assert result["code"] == "JOB_ALREADY_RUNNING"


def test_run_all_generates_unique_bulk_execution_id(app, monkeypatch):
    monkeypatch.setattr(
        "app.services.execution_service.requests.get",
        lambda *_args, **_kwargs: _Response(200, "ok"),
    )

    with app.app_context():
        _create_job()
        _create_job()

        summary = ExecutionService.run_all_active_jobs()

    assert summary["count"] == 2
    assert summary["bulk_execution_id"].startswith("bulk-")

    seen_bulk_ids = set()
    for result in summary["results"]:
        seen_bulk_ids.add(result["bulk_execution_id"])
        for execution in result["executions"]:
            assert execution["bulk_execution_id"] == summary["bulk_execution_id"]

    assert len(seen_bulk_ids) == 1
