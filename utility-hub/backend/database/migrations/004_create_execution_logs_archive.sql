CREATE TABLE IF NOT EXISTS execution_logs_archive (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_log_id INTEGER NOT NULL,
    cron_job_id INTEGER NOT NULL,
    bulk_execution_id VARCHAR(64),
    execution_no INTEGER NOT NULL DEFAULT 1,
    status VARCHAR(30) NOT NULL,
    status_code INTEGER,
    response_time FLOAT,
    response_body TEXT,
    error_message TEXT,
    executed_at DATETIME NOT NULL,
    archived_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_execution_logs_archive_original_log_id
    ON execution_logs_archive(original_log_id);

CREATE INDEX IF NOT EXISTS idx_execution_logs_archive_executed_at
    ON execution_logs_archive(executed_at);
