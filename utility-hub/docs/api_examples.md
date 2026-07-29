# Utility Hub API Examples

## Cron Automation APIs

### Create Cron Job

```bash
curl -X POST http://localhost:5000/api/cron \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Archive Return Order Logs",
    "url": "https://web7.omnirps.com/cron/cron_delete_and_archive_log_table_data/return_order",
    "execution_count": 5,
    "schedule_type": "daily",
    "is_active": true,
    "description": "Archives return_order logs"
  }'
```

### Create Custom-Scheduled Cron Job

```bash
curl -X POST http://localhost:5000/api/cron \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Every 15 Minutes",
    "url": "https://example.com/cron",
    "execution_count": 1,
    "schedule_type": "custom",
    "schedule_expression": "*/15 * * * *",
    "is_active": true
  }'
```

### List Cron Jobs

```bash
curl http://localhost:5000/api/cron
```

### Run Single Cron Job

```bash
curl -X POST http://localhost:5000/api/run/1
```

### Update Cron Job Schedule

```bash
curl -X PUT http://localhost:5000/api/cron/1 \
  -H "Content-Type: application/json" \
  -d '{
    "schedule_type": "hourly",
    "schedule_expression": null
  }'
```

### Run All Active Cron Jobs

```bash
curl -X POST http://localhost:5000/api/run-all
```

### Execution History

```bash
curl http://localhost:5000/api/history?limit=50
```

### Dashboard

```bash
curl http://localhost:5000/api/dashboard
```

### Report

```bash
curl http://localhost:5000/api/report?period=daily
curl http://localhost:5000/api/report?period=weekly
curl http://localhost:5000/api/report?period=monthly
```

### Report Trend

```bash
curl "http://localhost:5000/api/report/trend?days=14"
curl "http://localhost:5000/api/report/trend?days=14&cron_job_id=1"
```

### Report Errors Summary

```bash
curl "http://localhost:5000/api/report/errors?period=weekly&limit=10"
curl "http://localhost:5000/api/report/errors?period=weekly&cron_job_id=1&limit=5"
```

### Report CSV Export

```bash
curl -L "http://localhost:5000/api/report/export?period=daily" -o cron_report_daily.csv
```

## Web UI Pages

Open in browser:

```text
http://localhost:5000/dashboard
http://localhost:5000/cron-jobs
http://localhost:5000/history
http://localhost:5000/history-cleanup
http://localhost:5000/reports
http://localhost:5000/address-validation
http://localhost:5000/url-monitoring
```

## Address Validation API

```bash
curl -X POST http://localhost:5000/api/address/validate \
  -H "Content-Type: application/json" \
  -d '{
    "BuildingName": "Bastia Hill",
    "StreetAddress": "22 Bastia Avenue",
    "Suburb": "BASTIA HILL",
    "City": "WHANGANUI",
    "PostCode": "4500",
    "CountryCode": "NZ"
  }'

curl "http://localhost:5000/api/address/history?limit=20"
```

## URL Monitoring API

```bash
curl -X POST http://localhost:5000/api/monitoring/urls \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com","notes":"homepage","is_active":true}'

curl "http://localhost:5000/api/monitoring/urls"

curl -X POST http://localhost:5000/api/monitoring/execute \
  -H "Content-Type: application/json" \
  -d '{"trigger_type":"MANUAL","initiated_by":"api-user"}'

curl "http://localhost:5000/api/monitoring/reports?limit=10"
curl "http://localhost:5000/api/monitoring/scheduler/status"
curl -X POST http://localhost:5000/api/monitoring/scheduler/run-now \
  -H "Content-Type: application/json" \
  -d '{"initiated_by":"ops-user"}'
```

## Health API

```bash
curl "http://localhost:5000/health"
```

## History Cleanup (Web UI)

Use the History Cleanup page to move old records from `execution_logs` to `execution_logs_archive`.

Retention options:

- Archive 15 days old records
- Archive 1 month old record (default)
- Archive 3 months old records
- Archive 6 months old records

## API Auth Header Examples (When Enabled)

```bash
curl http://localhost:5000/api/cron -H "X-API-Key: your_api_key"
curl http://localhost:5000/api/cron -H "Authorization: Bearer your_api_key"
```

## Web Login (When Enabled)

```text
GET  http://localhost:5000/login
POST http://localhost:5000/login
POST http://localhost:5000/logout
```
