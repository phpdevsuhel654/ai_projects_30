# Utility Hub Architecture

## Overview

Utility Hub is a Flask application with modular services for cron automation, address validation, URL monitoring, and health checks.

## Layered Design

- Controllers: Parse HTTP input and return API/web responses
- Services: Execute business logic and orchestration
- Repositories: Persist and query data via SQLAlchemy
- Models: Define database entities and relationships
- Scheduler: Run background jobs with APScheduler
- Reports: Aggregate analytics and export-friendly datasets

## Integrated Modules

- Cron Automation Core
	- Cron CRUD, run single, run all, history, reporting
- Address Validation
	- Payload normalization, provider lookup, confidence scoring, validation history
- URL Monitoring
	- URL registry, active endpoint checks, scheduler execution, run summaries and details
- Health
	- Lightweight runtime health endpoint

## Request Lifecycle

1. Client sends API or web request
2. Controller validates and normalizes request data
3. Service executes module logic
4. Repository reads/writes the database
5. Service returns response DTO
6. Controller returns JSON or HTML

## UI and Theme Architecture

1. Shared shell is rendered from `backend/app/templates/base.html`
2. Global visual system is applied from `backend/app/static/css/app.css`
3. Brand assets are loaded from `backend/app/static/logo.png` and `backend/app/static/favicon.svg`
4. Pages follow shared card, table-grid, badge, and button patterns

## Module Flows

### Cron Execution Flow

1. Cron metadata is stored in `cron_jobs`
2. Manual or scheduled trigger starts execution
3. URL requests are executed with timeout/retry handling
4. Results are written to `execution_logs`
5. Dashboard and reports aggregate run outcomes

### Address Validation Flow

1. User submits JSON in `/address-validation` or `POST /api/address/validate`
2. Service maps aliases to canonical fields and validates required fields
3. Service queries Nominatim and computes confidence/status
4. Validation record is stored in `address_validations`
5. Result is returned to API/UI and listed in history grid

### URL Monitoring Flow

1. URLs are managed in `/url-monitoring` or `/api/monitoring/urls`
2. Manual run or scheduler run executes active URL checks
3. DNS, HTTP status, HTTPS validity, and response time are captured
4. Summary is saved in `execution_history`; URL-level rows in `execution_details`
5. Latest results and execution history are shown in grid format

### History Cleanup Flow

1. User opens `/history-cleanup`
2. User selects retention window
3. Old rows from `execution_logs` are copied to `execution_logs_archive`
4. Archived rows are removed from active history
5. UI displays archived row count

## Data Migration Flow (monitor-system to Utility Hub)

1. One-time import script reads source SQLite
2. Address validations are deduplicated and inserted
3. Monitored URLs are merged by URL uniqueness
4. Execution history/details are remapped to merged URL IDs
5. Import summary is printed for verification
