# Development Roadmap

## Phase 1: Foundation (completed)

- Project scaffolding and clean folder structure.
- Flask app factory and environment-based config.
- SQLAlchemy models and SQLite schema migration SQL.
- Cron CRUD APIs.
- Manual run, run-all, history, dashboard, and report APIs.
- Seed data and baseline tests.

## Phase 2: Scheduler Engine (completed)

- APScheduler trigger mapping for daily/hourly/custom.
- Prevent duplicate execution with run locks.
- Retry strategy with exponential backoff.

## Phase 2.5: Scheduler Hardening (next)

- Persist scheduler metadata and last-run state.
- Add misfire handling and configurable grace windows.
- Add pause/resume scheduler controls via API.

## Phase 3: UI Dashboard (completed)

- Bootstrap dashboard cards and tables.
- Cron management forms and execution controls.
- History listing with quick row limit filters.

## Phase 4: Advanced Reporting (completed)

- Downloadable CSV report export.
- Error clustering and trend analysis.
- Time-window and job-level drilldowns.

## Phase 5: Notifications and Hardening (completed)

- Failure alerts and execution summary notifications.
- Optional API authentication and web login protection.
- Security response headers and hardened session defaults.
- Expanded unit/integration test coverage.

## Phase 6: Platform Readiness (next)

- CI pipeline and deployment profile.
- Containerized production runtime.
- Operational runbook and health-alert integration.
