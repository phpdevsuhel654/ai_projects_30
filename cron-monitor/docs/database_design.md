# Database Design

## Table: cron_jobs

- id (PK)
- name
- url
- execution_count
- schedule_type
- is_active
- description
- created_at
- updated_at

## Table: execution_logs

- id (PK)
- cron_job_id (FK -> cron_jobs.id)
- bulk_execution_id
- execution_no
- status
- status_code
- response_time
- response_body
- error_message
- executed_at

## Table: execution_logs_archive

- id (PK)
- original_log_id
- cron_job_id
- bulk_execution_id
- execution_no
- status
- status_code
- response_time
- response_body
- error_message
- executed_at
- archived_at

## Indexes

- `execution_logs.cron_job_id`
- `execution_logs.executed_at`
- `execution_logs.bulk_execution_id`
- `execution_logs_archive.original_log_id`
- `execution_logs_archive.executed_at`

## Notes

- `execution_count` supports multiple runs per cron URL.
- `schedule_type` currently supports `daily`, `hourly`, and `custom` labels.
- Response body is capped before storage in service layer.
- Old execution history is archived from `execution_logs` to `execution_logs_archive` using retention rules.
