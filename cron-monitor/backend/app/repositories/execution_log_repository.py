from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import joinedload

from app.models import ExecutionLog
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
