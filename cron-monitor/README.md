# Cron Job URL Automation & Monitoring System

Production-ready Flask-based system to manage, execute, monitor, and report cron job URLs.

## 1) High-Level Architecture

- Backend framework: Flask (App Factory pattern)
- Data layer: SQLite + SQLAlchemy
- Scheduler layer: APScheduler (foundation added)
- API layer: RESTful endpoints
- Monitoring: Execution logs, dashboard metrics, period-based reporting

Detailed architecture: `docs/architecture.md`

## 2) Database Design

- `cron_jobs`: cron job definitions and schedule metadata
- `execution_logs`: every execution attempt with response data and errors

Detailed schema: `docs/database_design.md`

## 3) Folder Structure

```text
cron-monitor/
├── backend/
│   ├── app/
│   │   ├── config/
│   │   ├── controllers/
│   │   ├── models/
│   │   ├── reports/
│   │   ├── repositories/
│   │   ├── scheduler/
│   │   ├── services/
│   │   ├── static/
│   │   ├── templates/
│   │   └── utils/
│   ├── database/
│   │   ├── migrations/
│   │   └── seed_data.py
│   ├── logs/
│   ├── tests/
│   ├── requirements.txt
│   └── run.py
├── docs/
│   ├── architecture.md
│   ├── database_design.md
│   ├── roadmap.md
│   └── api_examples.md
└── README.md
```

## 4) Development Roadmap

- Phase 1: Foundation (implemented)
- Phase 2: Scheduler engine and duplicate-run prevention (implemented)
- Phase 3: Bootstrap UI dashboard (implemented)
- Phase 4: Advanced report exports and trends (implemented)
- Phase 5: Notifications and security hardening (implemented)

Roadmap details: `docs/roadmap.md`

## 5) Phase-1 Project Setup

### Prerequisites

- Python 3.11+

### Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python run.py
```

### Seed Sample Data

```bash
cd backend
python database/seed_data.py
```

### Run Tests

```bash
cd backend
pytest -q
```

### Local Test Credentials

Use these credentials only for local development/testing:

```text
Login URL: http://localhost:5000/login
Username: admin
Password: Admin@12345
```

## Implemented APIs (Phase 1)

- `POST /api/cron`
- `GET /api/cron`
- `GET /api/cron/<id>`
- `PUT /api/cron/<id>`
- `DELETE /api/cron/<id>`
- `POST /api/run/<id>`
- `POST /api/run-all`
- `GET /api/history`
- `GET /api/report?period=daily|weekly|monthly`
- `GET /api/dashboard`
- `GET /health`

API examples: `docs/api_examples.md`

## Phase 2 Additions

- APScheduler auto-registers active jobs on app startup.
- Supported schedule types: `hourly`, `daily`, `custom`.
- For `custom`, pass `schedule_expression` using 5-part cron format.
- Retry with exponential backoff for failed URL calls.
- Overlap prevention ensures a cron job cannot execute concurrently.

Example custom schedule payload:

```json
{
	"name": "Every 15 minutes",
	"url": "https://example.com/cron",
	"execution_count": 1,
	"schedule_type": "custom",
	"schedule_expression": "*/15 * * * *",
	"is_active": true
}
```

## Phase 3 Additions

- Server-rendered Bootstrap UI pages added:
	- `/dashboard`
	- `/cron-jobs`
	- `/history`
	- `/reports`
- UI supports:
	- Add cron jobs via form
	- Enable/disable jobs
	- Run single job from UI
	- Delete jobs
	- Run all active jobs from dashboard
	- View recent logs and report summaries

## Phase 4 Additions

- Report drilldowns with filters:
	- `period`
	- `cron_job_id`
	- `start_at` / `end_at` (ISO datetime)
- Trend analytics endpoint with configurable day window.
- Error summary endpoint with top failure groups.
- CSV export endpoint for report data.

New APIs:

- `GET /api/report/trend?days=7&cron_job_id=<id>`
- `GET /api/report/errors?period=daily&limit=10&cron_job_id=<id>`
- `GET /api/report/export?period=daily&cron_job_id=<id>`

Web reports page now includes:

- Advanced filter form
- CSV export button
- Trend table
- Top errors table

## Phase 5 Additions

- Notifications:
	- Failed cron execution alerts.
	- Run-all execution summary notifications.
	- Optional webhook delivery (falls back to structured app logs).

- Security hardening:
	- Optional API authentication with `X-API-Key` or `Authorization: Bearer <key>`.
	- Optional web login protection for UI routes.
	- Security headers middleware:
		- `X-Content-Type-Options`
		- `X-Frame-Options`
		- `Referrer-Policy`
		- `Permissions-Policy`
		- `Content-Security-Policy`

### Phase 5 Configuration

```env
NOTIFICATIONS_ENABLED=false
NOTIFICATION_WEBHOOK_URL=
NOTIFICATION_TIMEOUT_SECONDS=5
NOTIFY_ON_FAILURE=true
NOTIFY_ON_SUMMARY=true

API_AUTH_ENABLED=false
API_AUTH_KEY=

WEB_AUTH_ENABLED=false
WEB_AUTH_USERNAME=admin
WEB_AUTH_PASSWORD=changeme
SESSION_COOKIE_SECURE=false
```

### Auth Example

```bash
curl http://localhost:5000/api/cron -H "X-API-Key: <your-key>"
curl http://localhost:5000/api/cron -H "Authorization: Bearer <your-key>"
```
