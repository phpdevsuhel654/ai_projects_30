from datetime import datetime, timezone

from app.utils.extensions import db


class ExecutionLogArchive(db.Model):
    __tablename__ = "execution_logs_archive"

    id = db.Column(db.Integer, primary_key=True)
    original_log_id = db.Column(db.Integer, nullable=False, index=True)
    cron_job_id = db.Column(db.Integer, nullable=False)
    bulk_execution_id = db.Column(db.String(64), nullable=True)
    execution_no = db.Column(db.Integer, nullable=False, default=1)
    status = db.Column(db.String(30), nullable=False)
    status_code = db.Column(db.Integer, nullable=True)
    response_time = db.Column(db.Float, nullable=True)
    response_body = db.Column(db.Text, nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    executed_at = db.Column(db.DateTime, nullable=False)
    archived_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "original_log_id": self.original_log_id,
            "cron_job_id": self.cron_job_id,
            "bulk_execution_id": self.bulk_execution_id,
            "execution_no": self.execution_no,
            "status": self.status,
            "status_code": self.status_code,
            "response_time": self.response_time,
            "response_body": self.response_body,
            "error_message": self.error_message,
            "executed_at": self.executed_at.isoformat() if self.executed_at else None,
            "archived_at": self.archived_at.isoformat() if self.archived_at else None,
        }