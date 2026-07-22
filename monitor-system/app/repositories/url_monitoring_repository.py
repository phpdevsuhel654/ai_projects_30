from __future__ import annotations

from app import db
from app.models.url_monitoring import ExecutionDetail, ExecutionHistory, MonitoredURL


class URLMonitoringRepository:
    def add_url(self, url: str, notes: str | None = None, is_active: bool = True) -> MonitoredURL:
        row = MonitoredURL(url=url, notes=notes, is_active=is_active)
        db.session.add(row)
        db.session.commit()
        return row

    def get_url(self, url_id: int) -> MonitoredURL | None:
        return db.session.get(MonitoredURL, url_id)

    def get_by_url(self, url: str) -> MonitoredURL | None:
        return MonitoredURL.query.filter_by(url=url).first()

    def update_url(
        self,
        url_id: int,
        url: str | None = None,
        notes: str | None = None,
        is_active: bool | None = None,
    ) -> MonitoredURL | None:
        row = self.get_url(url_id)
        if row is None:
            return None

        if url is not None:
            row.url = url
        if notes is not None:
            row.notes = notes
        if is_active is not None:
            row.is_active = is_active

        db.session.commit()
        return row

    def delete_url(self, url_id: int) -> bool:
        row = self.get_url(url_id)
        if row is None:
            return False
        db.session.delete(row)
        db.session.commit()
        return True

    def list_urls(self, active_only: bool = False) -> list[MonitoredURL]:
        query = MonitoredURL.query
        if active_only:
            query = query.filter_by(is_active=True)
        return query.order_by(MonitoredURL.id.asc()).all()

    def create_execution(
        self,
        trigger_type: str,
        started_at,
        ended_at,
        total_duration_ms: int,
        total_urls: int,
        success_count: int,
        failed_count: int,
        overall_status: str,
        initiated_by: str | None,
        details: list[dict],
    ) -> ExecutionHistory:
        history = ExecutionHistory(
            trigger_type=trigger_type,
            started_at=started_at,
            ended_at=ended_at,
            total_duration_ms=total_duration_ms,
            total_urls=total_urls,
            success_count=success_count,
            failed_count=failed_count,
            overall_status=overall_status,
            initiated_by=initiated_by,
        )
        db.session.add(history)
        db.session.flush()

        for detail in details:
            db.session.add(
                ExecutionDetail(
                    execution_history_id=history.id,
                    monitored_url_id=detail["monitored_url_id"],
                    dns_resolved=detail["dns_resolved"],
                    http_status_code=detail["http_status_code"],
                    https_valid=detail["https_valid"],
                    response_time_ms=detail["response_time_ms"],
                    availability_status=detail["availability_status"],
                    error_message=detail["error_message"],
                    checked_at=detail["checked_at"],
                )
            )

        db.session.commit()
        return history

    def list_execution_history(self, limit: int = 20) -> list[ExecutionHistory]:
        safe_limit = max(1, min(limit, 100))
        return (
            ExecutionHistory.query.order_by(ExecutionHistory.started_at.desc())
            .limit(safe_limit)
            .all()
        )

    def get_execution(self, execution_id: int) -> ExecutionHistory | None:
        return db.session.get(ExecutionHistory, execution_id)
