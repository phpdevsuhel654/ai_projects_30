# Utility Hub Roadmap

## Phase 1: Foundation (Completed)

- Project scaffolding and clean folder structure.
- Flask app factory and environment-based config.
- SQLAlchemy models and SQLite schema migration SQL.
- Cron CRUD APIs.
- Manual run, run-all, history, dashboard, and report APIs.
- Seed data and baseline tests.

## Phase 2: Scheduler Engine (Completed)

- APScheduler trigger mapping for daily/hourly/custom.
- Prevent duplicate execution with run locks.
- Retry strategy with exponential backoff.

## Phase 2.5: Scheduler Hardening (Next)

- Persist scheduler metadata and last-run state.
- Add misfire handling and configurable grace windows.
- Add pause/resume scheduler controls via API.

## Phase 3: UI Dashboard (Completed)

- Bootstrap dashboard cards and tables.
- Cron management forms and execution controls.
- History listing with quick row limit filters.
- History cleanup page with retention-based archive move to archive table.

## Phase 4: Advanced Reporting (Completed)

- Downloadable CSV report export.
- Error clustering and trend analysis.
- Time-window and job-level drilldowns.

## Phase 5: Notifications and Hardening (Completed)

- Failure alerts and execution summary notifications.
- Optional API authentication and web login protection.
- Security response headers and hardened session defaults.
- Expanded unit/integration test coverage.

## Phase 5.5: Module Integration and UX Standardization (Completed)

- Integrated Address Validation module (API + web UI + history).
- Integrated URL Monitoring module (URL CRUD + health checks + scheduler + reports).
- Added Health endpoint access in global navigation.
- Added merged dashboard summary metrics for integrated modules.
- Standardized global branding (logo, favicon, title text).
- Applied production-style visual standards for shared layout, cards, grids, and button system.

## Phase 5.6: Data Merge Enablement (Completed)

- Added one-time import utility to merge monitor-system data into Utility Hub.
- Added deduplication and ID remapping logic for address and URL monitoring records.
- Added import run instructions and verification outputs.

## Phase 6: Platform Readiness (Next)

- CI pipeline and deployment profile.
- Containerized production runtime.
- Operational runbook and health-alert integration.
