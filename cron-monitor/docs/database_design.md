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
- execution_no
- status
- status_code
- response_time
- response_body
- error_message
- executed_at

## Indexes

- `execution_logs.cron_job_id`
- `execution_logs.executed_at`

## Notes

- `execution_count` supports multiple runs per cron URL.
- `schedule_type` currently supports `daily`, `hourly`, and `custom` labels.
- Response body is capped before storage in service layer.
