from datetime import datetime, timedelta, timezone

from app.models import CronJob, ExecutionLog, ExecutionLogArchive
from app.utils.extensions import db


def test_dashboard_page_loads(client):
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert b"Execution Dashboard" in response.data


def test_cron_jobs_page_loads(client):
    response = client.get("/cron-jobs")
    assert response.status_code == 200
    assert b"Add Cron Job" in response.data


def test_create_cron_job_from_web_form(client):
    form_data = {
        "name": "Web Cron",
        "url": "https://example.com/cron",
        "execution_count": "1",
        "schedule_type": "daily",
        "schedule_expression": "",
        "description": "created from web",
        "is_active": "on",
    }

    response = client.post("/cron-jobs", data=form_data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Cron job added successfully." in response.data
    assert b"Web Cron" in response.data


def test_edit_cron_job_from_web_form(client):
    create_data = {
        "form_mode": "create",
        "name": "Editable Cron",
        "url": "https://example.com/old",
        "execution_count": "1",
        "schedule_type": "daily",
        "schedule_expression": "",
        "description": "old description",
        "is_active": "on",
    }
    create_response = client.post("/cron-jobs", data=create_data, follow_redirects=True)
    assert create_response.status_code == 200

    list_response = client.get("/api/cron")
    jobs = list_response.get_json()
    target = next(item for item in jobs if item["name"] == "Editable Cron")

    update_data = {
        "form_mode": "edit",
        "cron_id": str(target["id"]),
        "name": "Edited Cron",
        "url": "https://example.com/new",
        "execution_count": "2",
        "schedule_type": "hourly",
        "schedule_expression": "",
        "description": "updated description",
    }

    update_response = client.post("/cron-jobs", data=update_data, follow_redirects=True)
    assert update_response.status_code == 200
    assert b"Cron job updated successfully." in update_response.data
    assert b"Edited Cron" in update_response.data


def test_history_cleanup_page_default_selection(client):
    response = client.get("/history-cleanup")
    assert response.status_code == 200
    assert b"Execution History Cleanup" in response.data
    assert b'value="1m" selected' in response.data


def test_history_cleanup_archives_only_old_records(app, client):
    with app.app_context():
        job = CronJob(
            name="Cleanup Cron",
            url="https://example.com/cleanup",
            execution_count=1,
            schedule_type="daily",
            is_active=True,
        )
        db.session.add(job)
        db.session.commit()

        old_log = ExecutionLog(
            cron_job_id=job.id,
            execution_no=1,
            status="success",
            executed_at=datetime.now(timezone.utc) - timedelta(days=40),
        )
        recent_log = ExecutionLog(
            cron_job_id=job.id,
            execution_no=1,
            status="success",
            executed_at=datetime.now(timezone.utc) - timedelta(days=10),
        )
        db.session.add_all([old_log, recent_log])
        db.session.commit()
        old_log_id = old_log.id
        recent_log_id = recent_log.id

    response = client.post(
        "/history-cleanup",
        data={"retention": "1m"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Archived 1 old execution history record(s)." in response.data

    with app.app_context():
        all_logs = ExecutionLog.query.order_by(ExecutionLog.executed_at.asc()).all()
        assert len(all_logs) == 1
        assert all_logs[0].id == recent_log_id

        archived_logs = ExecutionLogArchive.query.all()
        assert len(archived_logs) == 1
        assert archived_logs[0].original_log_id == old_log_id
