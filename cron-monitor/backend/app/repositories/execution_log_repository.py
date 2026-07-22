from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import joinedload

from app.models import ExecutionLog, ExecutionLogArchive
from app.utils.extensions import db


class ExecutionLogRepository:
    @staticmethod
    def create(log: ExecutionLog) -> ExecutionLog:
        db.session.add(log)
        db.session.commit()
        return log

    @staticmethod
    def list_recent(limit: int = 100) -> list[ExecutionLog]:
        return (
            ExecutionLog.query.options(joinedload(ExecutionLog.cron_job))
            .order_by(ExecutionLog.executed_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def search(
        limit: int = 100,
        cron_job_id: int | None = None,
        bulk_execution_id: str | None = None,
        status: str | None = None,
        start_at: datetime | None = None,
        end_at: datetime | None = None,
    ) -> list[ExecutionLog]:
        query = ExecutionLog.query.options(joinedload(ExecutionLog.cron_job))

        if cron_job_id is not None:
            query = query.filter(ExecutionLog.cron_job_id == cron_job_id)
        if bulk_execution_id:
            query = query.filter(ExecutionLog.bulk_execution_id == bulk_execution_id)
        if status:
            query = query.filter(ExecutionLog.status == status)
        if start_at is not None:
            query = query.filter(ExecutionLog.executed_at >= start_at)
        if end_at is not None:
            query = query.filter(ExecutionLog.executed_at <= end_at)

        return query.order_by(ExecutionLog.executed_at.desc()).limit(limit).all()

    @staticmethod
    def aggregate_counts() -> dict:
        total = db.session.query(func.count(ExecutionLog.id)).scalar() or 0
        success = (
            db.session.query(func.count(ExecutionLog.id))
            .filter(ExecutionLog.status == "success")
            .scalar()
            or 0
        )
        failure = (
            db.session.query(func.count(ExecutionLog.id))
            .filter(ExecutionLog.status == "failure")
            .scalar()
            or 0
        )
        avg_response_time = db.session.query(func.avg(ExecutionLog.response_time)).scalar() or 0
        last_execution = db.session.query(func.max(ExecutionLog.executed_at)).scalar()

        return {
            "total_executions": int(total),
            "success_count": int(success),
            "failure_count": int(failure),
            "avg_response_time": float(avg_response_time),
            "last_execution_time": last_execution.isoformat() if isinstance(last_execution, datetime) else None,
        }

    @staticmethod
    def archive_executed_before(cutoff: datetime) -> int:
        logs_to_archive = (
            ExecutionLog.query.filter(ExecutionLog.executed_at < cutoff)
            .order_by(ExecutionLog.id.asc())
            .all()
        )
        if not logs_to_archive:
            return 0

        archived_at = datetime.now(timezone.utc)
        archive_rows = [
            ExecutionLogArchive(
                original_log_id=log.id,
                cron_job_id=log.cron_job_id,
                bulk_execution_id=log.bulk_execution_id,
                execution_no=log.execution_no,
                status=log.status,
                status_code=log.status_code,
                response_time=log.response_time,
                response_body=log.response_body,
                error_message=log.error_message,
                executed_at=log.executed_at,
                archived_at=archived_at,
            )
            for log in logs_to_archive
        ]

        db.session.bulk_save_objects(archive_rows)
        ExecutionLog.query.filter(ExecutionLog.executed_at < cutoff).delete(synchronize_session=False)
        db.session.commit()
        return len(logs_to_archive)
