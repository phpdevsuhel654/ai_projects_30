ALTER TABLE execution_logs ADD COLUMN bulk_execution_id VARCHAR(64);
CREATE INDEX IF NOT EXISTS idx_execution_logs_bulk_execution_id ON execution_logs(bulk_execution_id);
