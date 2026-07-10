CREATE TABLE IF NOT EXISTS cron_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(150) NOT NULL,
    url VARCHAR(500) NOT NULL,
    execution_count INTEGER NOT NULL DEFAULT 1,
    schedule_type VARCHAR(50) NOT NULL DEFAULT 'daily',
    schedule_expression VARCHAR(120),
    is_active BOOLEAN NOT NULL DEFAULT 1,
    description TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS execution_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cron_job_id INTEGER NOT NULL,
    bulk_execution_id VARCHAR(64),
    execution_no INTEGER NOT NULL DEFAULT 1,
    status VARCHAR(30) NOT NULL,
    status_code INTEGER,
    response_time FLOAT,
    response_body TEXT,
    error_message TEXT,
    executed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cron_job_id) REFERENCES cron_jobs(id)
);

CREATE INDEX IF NOT EXISTS idx_execution_logs_cron_job_id ON execution_logs(cron_job_id);
CREATE INDEX IF NOT EXISTS idx_execution_logs_executed_at ON execution_logs(executed_at);
CREATE INDEX IF NOT EXISTS idx_execution_logs_bulk_execution_id ON execution_logs(bulk_execution_id);
