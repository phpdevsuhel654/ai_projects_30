# Utility Hub: User Understanding Guide

## 1. What this app does

Utility Hub helps you manage cron URL executions and operational utility modules from one place.

You can:
- Add, edit, enable, disable, and delete cron jobs.
- Run one cron job or run all active jobs in bulk.
- Track execution history with filters.
- Archive old execution history records by retention period.
- View daily/weekly/monthly reports.
- Identify failed runs and response details quickly.
- Validate and normalize addresses using Address Validation.
- Monitor endpoint health using URL Monitoring.

## 2. Main Workflow

1. Add cron jobs in the Cron Jobs page.
2. Set execution count and schedule type.
3. Run jobs manually (single or all active).
4. Review execution history and response output.
5. Archive old history records from History Cleanup when needed.
6. Analyze reports for success/failure trends.

## 3. Pages and Their Purpose

### Dashboard
- Shows summary metrics:
  - Total URLs
  - Active URLs
  - Total Executions
  - Success %
  - Address Validations
  - Monitored URLs
- Has a **Run All Active** action
- Shows recent executions.

### Cron Jobs
- Create new cron jobs.
- Edit existing cron jobs.
- Run a job instantly.
- Enable/disable jobs.
- Delete jobs

### Execution History
- Search/filter by:
  - Job name
  - Bulk execution ID
  - Status (success/failure)
  - Execution date-time range
  - Rows limit (up to 500)
- Shows:
  - Job name
  - Status and status code
  - Response time
  - Response body (if available)
  - Executed timestamp

### History Cleanup
- Open the page from top menu: `/history-cleanup`.
- Select archive retention window:
  - Archive 15 days old records
  - Archive 1 month old record (default)
  - Archive 3 months old records
  - Archive 6 months old records
- Click Archive Records to move matching rows to archive table.
- Archived records are removed from active history table after move.

### Reports
- View period-based reports (daily/weekly/monthly).
- Filter by cron job and date-time range.
- Daily report defaults to last 1 day window.
- View trend and top error summary.
- Export report as CSV

### Address Validation
- Open `/address-validation`.
- Submit address payload as JSON.
- Review validation status, confidence score, and corrected address.
- Use execution-style validation history grid to track status, confidence, and validated timestamps.

### URL Monitoring
- Open `/url-monitoring`.
- Add or update monitored URLs.
- Run health checks manually.
- Review execution summary, per-URL details, and scheduler status.
- Use **Latest Execution Results** grid for URL-level status checks.
- Use **Execution History** grid for run-level summaries and timing.

### Health
- Health endpoint is available at `/health`.
- Use it for lightweight runtime checks and monitoring integration.

## 4. Cron Job Fields Explained

- **Name**: Friendly name of the cron task.
- **URL**: Endpoint to call.
- **Execution Count**: Number of times job runs in one trigger.
- **Schedule Type**:
  - hourly
  - daily
  - custom
- **Schedule Expression**: Required only for custom schedule (5-part cron format).
- **Active**: Whether scheduler should include this job.
- **Description**: Optional notes.

## 5. Bulk Execution ID

When you run all active jobs, the system generates one unique **Bulk Execution ID**.

Use this ID in Execution History to find all logs from the same run-all batch.

## 6. Status Interpretation

- **Success**: HTTP status code is in success range and execution completed.
- **Failure**: Request failed, retried, or final status was unsuccessful.

For failures, check:
- Error message
- Status code
- Response body (if present)

## 7. Typical Troubleshooting

### No data on dashboard/history
- Check if jobs were executed.
- Run one job manually from Cron Jobs.
- Refresh Dashboard/History.

### Frequent failures
- Verify URL is reachable from local machine.
- Confirm endpoint credentials/network access.
- Inspect status code and error details in History.

### Scheduler not running jobs
- Ensure job is active.
- Confirm schedule type/expression is valid.
- Verify app is running continuously.

## 8. One-Time Data Migration from monitor-system

Run from backend folder:

```bash
python scripts/import_monitor_system_data.py
```

Optional custom source database:

```bash
python scripts/import_monitor_system_data.py --source-db "D:/path/to/monitor_system.db"
```

## 9. Best Usage Tips

- Keep clear job names so filtering is easier.
- Use custom descriptions for operational notes.
- Use Bulk Execution ID to trace run-all events.
- Review daily report regularly for trend changes.

## 10. Quick Access

- Dashboard: `/dashboard`
- Cron Jobs: `/cron-jobs`
- Execution History: `/history`
- Reports: `/reports`
- History Cleanup: `/history-cleanup`
- Address Validation: `/address-validation`
- URL Monitoring: `/url-monitoring`
- Health: `/health`
