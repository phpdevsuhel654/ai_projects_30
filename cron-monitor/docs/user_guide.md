# Cron Monitor: User Understanding Guide

## 1. What this app does

Cron Monitor helps you manage and monitor cron URL executions from one place.

You can:
- Add, edit, enable, disable, and delete cron jobs.
- Run one cron job or run all active jobs in bulk.
- Track execution history with filters.
- View daily/weekly/monthly reports.
- Identify failed runs and response details quickly.

## 2. Main workflow

1. Add cron jobs in the Cron Jobs page.
2. Set execution count and schedule type.
3. Run jobs manually (single or all active).
4. Review execution history and response output.
5. Analyze reports for success/failure trends.

## 3. Pages and their purpose

### Dashboard
- Shows summary metrics:
  - Total URLs
  - Active URLs
  - Total Executions
  - Success %
- Has a **Run All Active** action.
- Shows recent executions.

### Cron Jobs
- Create new cron jobs.
- Edit existing cron jobs.
- Run a job instantly.
- Enable/disable jobs.
- Delete jobs.

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
  - Error message (if any)
  - Executed timestamp

### Reports
- View period-based reports (daily/weekly/monthly).
- Filter by cron job and date-time range.
- Daily report defaults to last 1 day window.
- View trend and top error summary.
- Export report as CSV.

## 4. Cron job fields explained

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

## 5. Bulk execution ID

When you run all active jobs, the system generates one unique **Bulk Execution ID**.

Use this ID in Execution History to find all logs from the same run-all batch.

## 6. Status interpretation

- **Success**: HTTP status code is in success range and execution completed.
- **Failure**: Request failed, retried, or final status was unsuccessful.

For failures, check:
- Error message
- Status code
- Response body (if present)

## 7. Typical troubleshooting

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

## 8. Best usage tips

- Keep clear job names so filtering is easier.
- Use custom descriptions for operational notes.
- Use Bulk Execution ID to trace run-all events.
- Review daily report regularly for trend changes.

## 9. Quick access

- Dashboard: `/dashboard`
- Cron Jobs: `/cron-jobs`
- Execution History: `/history`
- Reports: `/reports`
