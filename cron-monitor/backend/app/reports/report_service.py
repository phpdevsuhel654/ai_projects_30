from datetime import datetime, timedelta, timezone

from sqlalchemy import case, func

from app.models import CronJob, ExecutionLog
from app.utils.extensions import db


class ReportService:
    @staticmethod
    def _parse_iso_datetime(value: str | None) -> datetime | None:
        if not value:
            return None
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)

    @staticmethod
    def _get_start_datetime(period: str) -> datetime:
        now = datetime.now(timezone.utc)
        if period == "weekly":
            return now - timedelta(days=7)
        if period == "monthly":
            return now - timedelta(days=30)
        return now - timedelta(days=1)

    @staticmethod
    def _resolve_window(
        period: str,
        start_at: str | None = None,
        end_at: str | None = None,
    ) -> tuple[datetime, datetime]:
        now = datetime.now(timezone.utc)
        start = ReportService._parse_iso_datetime(start_at) or ReportService._get_start_datetime(period)
        end = ReportService._parse_iso_datetime(end_at) or now

        if end < start:
            start, end = end, start
        return start, end

    @staticmethod
    def summary(
        period: str = "daily",
        cron_job_id: int | None = None,
        start_at: str | None = None,
        end_at: str | None = None,
    ) -> dict:
        start, end = ReportService._resolve_window(period, start_at, end_at)

        query = (
            db.session.query(
                CronJob.id,
                CronJob.name,
                CronJob.url,
                func.count(ExecutionLog.id).label("run_count"),
                func.sum(case((ExecutionLog.status == "success", 1), else_=0)).label(
                    "success_count"
                ),
                func.sum(case((ExecutionLog.status == "failure", 1), else_=0)).label(
                    "failure_count"
                ),
                func.avg(ExecutionLog.response_time).label("avg_response_time"),
            )
            .join(ExecutionLog, ExecutionLog.cron_job_id == CronJob.id)
            .filter(ExecutionLog.executed_at >= start)
            .filter(ExecutionLog.executed_at <= end)
        )
        if cron_job_id is not None:
            query = query.filter(CronJob.id == cron_job_id)

        rows = query.group_by(CronJob.id, CronJob.name, CronJob.url).all()

        total_runs = 0
        total_success = 0
        total_failure = 0
        total_response_weighted = 0.0

        data = []
        for row in rows:
            run_count = int(row.run_count or 0)
            success_count = int(row.success_count or 0)
            failure_count = int(row.failure_count or 0)
            avg_response_time = float(row.avg_response_time or 0)

            total_runs += run_count
            total_success += success_count
            total_failure += failure_count
            total_response_weighted += avg_response_time * run_count

            data.append(
                {
                    "cron_job_id": row.id,
                    "name": row.name,
                    "url": row.url,
                    "run_count": run_count,
                    "success_count": success_count,
                    "failure_count": failure_count,
                    "avg_response_time": avg_response_time,
                }
            )

        overall_avg = (total_response_weighted / total_runs) if total_runs else 0
        success_percentage = (total_success / total_runs * 100) if total_runs else 0

        return {
            "period": period,
            "from": start.isoformat(),
            "to": end.isoformat(),
            "filters": {
                "cron_job_id": cron_job_id,
            },
            "totals": {
                "run_count": total_runs,
                "success_count": total_success,
                "failure_count": total_failure,
                "success_percentage": success_percentage,
                "avg_response_time": overall_avg,
            },
            "items": data,
        }

    @staticmethod
    def trend(
        days: int = 7,
        cron_job_id: int | None = None,
    ) -> dict:
        days = max(1, min(days, 90))
        end = datetime.now(timezone.utc)
        start = end - timedelta(days=days)

        query = (
            db.session.query(
                func.date(ExecutionLog.executed_at).label("day"),
                func.count(ExecutionLog.id).label("run_count"),
                func.sum(case((ExecutionLog.status == "success", 1), else_=0)).label(
                    "success_count"
                ),
                func.sum(case((ExecutionLog.status == "failure", 1), else_=0)).label(
                    "failure_count"
                ),
                func.avg(ExecutionLog.response_time).label("avg_response_time"),
            )
            .filter(ExecutionLog.executed_at >= start)
            .filter(ExecutionLog.executed_at <= end)
        )
        if cron_job_id is not None:
            query = query.filter(ExecutionLog.cron_job_id == cron_job_id)

        rows = query.group_by(func.date(ExecutionLog.executed_at)).order_by(
            func.date(ExecutionLog.executed_at)
        )

        items = []
        for row in rows:
            run_count = int(row.run_count or 0)
            success_count = int(row.success_count or 0)
            items.append(
                {
                    "date": str(row.day),
                    "run_count": run_count,
                    "success_count": success_count,
                    "failure_count": int(row.failure_count or 0),
                    "success_percentage": (success_count / run_count * 100)
                    if run_count
                    else 0,
                    "avg_response_time": float(row.avg_response_time or 0),
                }
            )

        return {
            "days": days,
            "from": start.isoformat(),
            "to": end.isoformat(),
            "filters": {
                "cron_job_id": cron_job_id,
            },
            "items": items,
        }

    @staticmethod
    def error_summary(
        period: str = "daily",
        cron_job_id: int | None = None,
        start_at: str | None = None,
        end_at: str | None = None,
        limit: int = 10,
    ) -> dict:
        start, end = ReportService._resolve_window(period, start_at, end_at)
        limit = max(1, min(limit, 100))

        normalized_error = func.coalesce(
            func.nullif(ExecutionLog.error_message, ""),
            "failure without error message",
        )

        query = (
            db.session.query(
                normalized_error.label("error_message"),
                func.count(ExecutionLog.id).label("occurrences"),
            )
            .filter(ExecutionLog.status == "failure")
            .filter(ExecutionLog.executed_at >= start)
            .filter(ExecutionLog.executed_at <= end)
        )
        if cron_job_id is not None:
            query = query.filter(ExecutionLog.cron_job_id == cron_job_id)

        rows = (
            query.group_by(normalized_error)
            .order_by(func.count(ExecutionLog.id).desc())
            .limit(limit)
            .all()
        )

        items = [
            {
                "error_message": row.error_message,
                "occurrences": int(row.occurrences or 0),
            }
            for row in rows
        ]

        return {
            "period": period,
            "from": start.isoformat(),
            "to": end.isoformat(),
            "filters": {
                "cron_job_id": cron_job_id,
                "limit": limit,
            },
            "items": items,
        }
