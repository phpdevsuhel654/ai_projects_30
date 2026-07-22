# Infrastructure Utility Portal

Production-ready learning project built step-by-step using Flask, SQLite, SQLAlchemy, and clean architecture patterns.

## Step 1 Completed

### 1. Objective
- Established system architecture baseline.
- Designed normalized database schema and ERD.
- Created production-style folder structure.
- Added initial dependency and environment setup.

### 2. Folder/File Creation
```
monitor-system/
|-- app/
|   |-- config/
|   |   |-- __init__.py
|   |   `-- settings.py
|   |-- models/
|   |   `-- __init__.py
|   |-- repositories/
|   |   `-- __init__.py
|   |-- routes/
|   |   |-- __init__.py
|   |   `-- health.py
|   |-- services/
|   |   `-- __init__.py
|   |-- static/
|   |-- templates/
|   |-- utils/
|   |   `-- __init__.py
|   `-- __init__.py
|-- database/
|-- docs/
|   |-- architecture.md
|   |-- database_design.md
|   `-- prompt.txt
|-- logs/
|-- migrations/
|-- tests/
|   `-- __init__.py
|-- .env
|-- .env.example
|-- app.py
`-- requirements.txt
```

### 3. Architecture Summary
- App factory pattern for environment-driven initialization.
- Layered design: Routes -> Services -> Repositories -> Models.
- SQLite database path controlled via environment variables.
- Flask-Migrate included for schema evolution.

### 4. Database Design
Detailed schema and ERD are available in:
- `docs/database_design.md`

### 5. Required Packages
Defined in `requirements.txt`:
- Flask
- Flask-SQLAlchemy
- Flask-Migrate
- SQLAlchemy
- requests
- APScheduler
- python-dotenv
- gunicorn
- pytest
- pytest-flask

### 6. Local Run (Smoke Test)
1. Create virtual environment
2. Install dependencies:
	- `pip install -r requirements.txt`
3. Run app:
	- `python app.py`
4. Verify health endpoint:
	- `GET http://127.0.0.1:5001/health`

## Next Step (pending approval)
Step 2 will implement SQLAlchemy models, repositories, and first Address Validation APIs using Nominatim.

## Step 2 Completed

### 1. Objective
- Delivered first production-style vertical slice for Address Validation module.

### 2. Folder/File Creation
- `app/models/address_validation.py`
- `app/repositories/address_validation_repository.py`
- `app/services/address_validation_service.py`
- `app/routes/address.py`
- `docs/step2_address_module.md`

### 3. APIs Added
- `POST /api/v1/address/validate`
- `GET /api/v1/address/history?limit=20`

### 4. Notes
- Uses Nominatim search API with User-Agent header.
- Persists original and corrected JSON payloads with confidence and status.

### 5. Test Procedure
See `docs/step2_address_module.md`.

## Step 3 Completed

### 1. Objective
- Added web UI for Address Validation using Jinja2 + Bootstrap 5.

### 2. Files
- `app/routes/address_ui.py`
- `app/templates/base.html`
- `app/templates/address_validation.html`
- `docs/step3_address_ui.md`

### 3. UI Routes
- `GET /`
- `GET/POST /address-validation`

### 4. Notes
- UI route reuses `AddressValidationService` (no duplicated business logic).
- Existing REST APIs remain unchanged.

### 5. Test Procedure
See `docs/step3_address_ui.md`.

## Step 4 Completed

### 1. Objective
- Implemented Feature 2 backend APIs for URL monitoring and execution reporting.

### 2. Files
- `app/models/url_monitoring.py`
- `app/repositories/url_monitoring_repository.py`
- `app/services/url_health_check_service.py`
- `app/routes/monitoring.py`
- `docs/step4_url_monitoring_api.md`

### 3. APIs Added
- `POST /api/v1/monitoring/urls`
- `GET /api/v1/monitoring/urls`
- `PUT /api/v1/monitoring/urls/<url_id>`
- `DELETE /api/v1/monitoring/urls/<url_id>`
- `POST /api/v1/monitoring/execute`
- `GET /api/v1/monitoring/reports`
- `GET /api/v1/monitoring/reports/<execution_id>`
- `GET /api/v1/monitoring/history`

### 4. Notes
- Execution stores summary in `execution_history` and per-URL rows in `execution_details`.
- Checks include DNS resolution, HTTP status, HTTPS validation, response time, and availability.

### 5. Test Procedure
See `docs/step4_url_monitoring_api.md`.

## Step 5 Completed

### 1. Objective
- Added and executed production-style migration workflow with Flask-Migrate.

### 2. Files
- `app/config/settings.py` (absolute DB path + dotenv loading)
- `.env` (Flask CLI vars)
- `.env.example` (Flask CLI vars)
- `migrations/alembic.ini`
- `migrations/env.py`
- `migrations/script.py.mako`
- `migrations/versions/447243cda2a3_initial_schema.py`
- `database/monitor_system.db`
- `docs/step5_migrations_and_db_init.md`

### 3. Commands Executed
- `python -m pip install -r requirements.txt`
- `flask db init`
- `flask db migrate -m "initial schema"`
- `flask db upgrade`

### 4. Notes
- SQLite connection path is now normalized to absolute path for CLI and Alembic stability.
- Initial migration includes all current module tables.

### 5. Test Procedure
See `docs/step5_migrations_and_db_init.md`.

## Step 6 Completed

### 1. Objective
- Implemented Feature 2 web dashboard UI for URL management and health check reporting.

### 2. Files
- `app/routes/monitoring_ui.py`
- `app/templates/monitoring_dashboard.html`
- `app/templates/base.html` (navigation links)
- `app/__init__.py` (UI blueprint registration)
- `docs/step6_monitoring_dashboard_ui.md`

### 3. UI Routes
- `GET /url-monitoring`
- `POST /url-monitoring/add`
- `POST /url-monitoring/<url_id>/update`
- `POST /url-monitoring/<url_id>/delete`
- `POST /url-monitoring/execute`

### 4. Dashboard Coverage
- Total URLs
- Active URLs
- Failed URLs
- Last Execution Time
- Execution History

### 5. Test Procedure
See `docs/step6_monitoring_dashboard_ui.md`.

## Step 7 Completed

### 1. Objective
- Added automated tests for URL monitoring service, APIs, and UI routes.

### 2. Files
- `tests/conftest.py`
- `tests/test_url_monitoring_service.py`
- `tests/test_monitoring_api.py`
- `tests/test_monitoring_ui.py`
- `docs/step7_automated_tests.md`

### 3. Verification
- Executed: `python -m pytest tests -q`
- Result: `6 passed`

### 4. Notes
- Replaced legacy SQLAlchemy Query.get usage with Session.get in repository layer.

### 5. Test Procedure
See `docs/step7_automated_tests.md`.

## Step 8 Completed

### 1. Objective
- Implemented centralized logging and request observability for production readiness.

### 2. Files
- `app/config/logging_config.py`
- `app/config/settings.py` (logging config values)
- `app/__init__.py` (logging setup + middleware registration)
- `app/services/address_validation_service.py` (service-level logs)
- `app/services/url_health_check_service.py` (service-level logs)
- `.env`
- `.env.example`
- `tests/test_logging.py`
- `docs/step8_logging_and_observability.md`

### 3. Logging Coverage
- Request/response logs with `X-Request-ID` and duration.
- Rotating file logs under `logs/`.
- Unhandled exception stack-trace logging.
- Business event logs for address validation and URL execution.

### 4. Verification
- Executed: `python -m pytest tests -q`
- Result: `9 passed`

### 5. Test Procedure
See `docs/step8_logging_and_observability.md`.

## Step 9 Completed

### 1. Objective
- Added automated scheduled execution for URL health checks using APScheduler.

### 2. Files
- `app/services/monitoring_scheduler_service.py`
- `app/config/settings.py` (scheduler config)
- `app/__init__.py` (scheduler startup)
- `app/routes/monitoring.py` (scheduler status + run-now APIs)
- `app/routes/monitoring_ui.py` (scheduler status binding)
- `app/templates/monitoring_dashboard.html` (scheduler status section)
- `.env`
- `.env.example`
- `tests/conftest.py`
- `tests/test_monitoring_api.py`
- `tests/test_monitoring_ui.py`
- `docs/step9_scheduled_monitoring.md`

### 3. Scheduler APIs Added
- `GET /api/v1/monitoring/scheduler/status`
- `POST /api/v1/monitoring/scheduler/run-now`

### 4. Notes
- Scheduler is disabled by default and enabled via environment variables.
- Default cron is set to `0 2 22-28 * sun` (4th Sunday style window).

### 5. Test Procedure
See `docs/step9_scheduled_monitoring.md`.
