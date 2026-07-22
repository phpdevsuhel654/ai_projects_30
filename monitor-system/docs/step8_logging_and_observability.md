# Step 8 - Centralized Logging and Observability

## 1) Objective
Add production-style logging for request lifecycle, application events, service operations, and unhandled errors.

## 2) Architecture Decisions
- Centralized logging setup in config layer to avoid duplicate logger wiring.
- Request middleware adds per-request ID and response duration for traceability.
- Rotating file handlers are used to keep log files bounded in size.
- Service layer emits business event logs for address validation and URL monitoring execution.

## 3) Folder/File Creation
- app/config/logging_config.py
- tests/test_logging.py
- docs/step8_logging_and_observability.md

## 4) Implementation Approach
- App startup:
  - setup_logging(app)
  - register_request_logging(app)
- Request logs include:
  - request_id
  - method
  - path
  - status_code
  - duration_ms
  - remote_addr
- Error handling:
  - unhandled exceptions are logged with stack traces
  - HTTPException responses (404, etc.) are preserved
- Service logs include:
  - address validation start/end
  - monitoring URL add/update/delete
  - monitoring execution start/end summary

## 5) Configuration
Configured via environment variables:
- LOGS_DIR
- LOG_LEVEL
- LOG_MAX_BYTES
- LOG_BACKUP_COUNT

Generated log files:
- logs/app.log
- logs/error.log

## 6) Testing Procedure
Run from project root:

```powershell
python -m pytest tests -q
```

Expected result after this step:
- 9 passed
