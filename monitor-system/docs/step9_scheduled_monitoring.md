# Step 9 - Scheduled URL Monitoring (APScheduler)

## 1) Objective
Enable automated URL health check execution on a recurring schedule so monitoring can run without manual intervention.

## 2) Architecture Decisions
- Use a dedicated scheduler service in the service layer to keep Flask routes and app factory clean.
- Keep scheduler optional and environment-driven (`MONITORING_SCHEDULER_ENABLED`) for safe local development.
- Use cron-based scheduling via APScheduler `CronTrigger.from_crontab`.
- Add operational visibility through API and dashboard scheduler status.

## 3) Folder/File Creation
- app/services/monitoring_scheduler_service.py
- docs/step9_scheduled_monitoring.md

## 4) Files Updated
- app/config/settings.py
- app/__init__.py
- app/routes/monitoring.py
- app/routes/monitoring_ui.py
- app/templates/monitoring_dashboard.html
- tests/conftest.py
- tests/test_monitoring_api.py
- tests/test_monitoring_ui.py
- .env
- .env.example
- README.md

## 5) Configuration
Environment variables:
- `MONITORING_SCHEDULER_ENABLED` (`true|false`)
- `MONITORING_SCHEDULER_CRON` (crontab format)
- `MONITORING_SCHEDULER_TIMEZONE` (IANA timezone, e.g. `UTC`)

Default values:
- enabled: `false`
- cron: `0 2 22-28 * sun` (4th Sunday pattern)
- timezone: `UTC`

## 6) APIs Added
- `GET /api/v1/monitoring/scheduler/status`
- `POST /api/v1/monitoring/scheduler/run-now`

## 7) UI Enhancement
- Dashboard now shows scheduler state, cron, timezone, next run time, and config errors.

## 8) Testing Procedure
Run from project root:

```powershell
python -m pytest tests -q
```

Expected after this step:
- Existing tests pass
- Scheduler endpoint and UI checks pass
