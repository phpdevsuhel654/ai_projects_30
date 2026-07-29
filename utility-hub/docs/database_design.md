# Utility Hub Database Design

## Core Tables

### cron_jobs

- id (PK)
- name
- url
- execution_count
- schedule_type
- is_active
- description
- created_at
- updated_at

### execution_logs

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

### execution_logs_archive

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

## Address Validation Tables

### address_validations

- id (PK)
- building_name
- street_address
- suburb
- city
- post_code
- country_code
- original_payload_json
- corrected_payload_json
- validation_status
- confidence_score
- provider_name
- provider_reference
- validated_at
- created_at

## URL Monitoring Tables

### monitored_urls

- id (PK)
- url (UNIQUE)
- is_active
- notes
- created_at
- updated_at

### execution_history

- id (PK)
- trigger_type
- started_at
- ended_at
- total_duration_ms
- total_urls
- success_count
- failed_count
- overall_status
- initiated_by

### execution_details

- id (PK)
- execution_history_id (FK -> execution_history.id)
- monitored_url_id (FK -> monitored_urls.id)
- dns_resolved
- http_status_code
- https_valid
- response_time_ms
- availability_status
- error_message
- checked_at

## Key Indexes

- `execution_logs.cron_job_id`
- `execution_logs.executed_at`
- `execution_logs.bulk_execution_id`
- `execution_logs_archive.original_log_id`
- `execution_logs_archive.executed_at`
- `address_validations.validation_status`
- `address_validations.validated_at`
- `monitored_urls.url`
- `monitored_urls.is_active`
- `execution_history.started_at`
- `execution_details.execution_history_id`
- `execution_details.monitored_url_id`
- `execution_details.availability_status`

## Relationship Summary

- `execution_logs.cron_job_id` -> `cron_jobs.id`
- `execution_details.execution_history_id` -> `execution_history.id`
- `execution_details.monitored_url_id` -> `monitored_urls.id`
- `address_validations` is standalone and stores original/corrected payload snapshots

## Operational Notes

- `execution_count` supports repeated calls for a single cron trigger
- `schedule_type` supports `daily`, `hourly`, and `custom`
- Response body storage is capped in service logic
- History cleanup moves old rows from `execution_logs` to `execution_logs_archive`

## Data Merge Notes

- Import monitor-system records using `backend/scripts/import_monitor_system_data.py`
- URL merge strategy uses URL uniqueness to avoid duplicates
- Execution history/details are remapped to merged URL IDs during import
