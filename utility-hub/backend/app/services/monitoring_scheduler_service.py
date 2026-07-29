from __future__ import annotations

import logging
import os
import threading
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.services.url_health_check_service import URLHealthCheckService


logger = logging.getLogger(__name__)


class MonitoringSchedulerService:
    def __init__(self) -> None:
        self._scheduler = BackgroundScheduler()
        self._lock = threading.Lock()
        self._job_id = "url_health_monitoring_job"
        self._last_error: str | None = None

    def start(self, app) -> None:
        if app.debug and os.getenv("WERKZEUG_RUN_MAIN") != "true":
            return

        if not app.config.get("MONITORING_SCHEDULER_ENABLED", False):
            logger.info("monitoring_scheduler_disabled")
            return

        cron_expression = app.config.get("MONITORING_SCHEDULER_CRON", "0 2 22-28 * sun")
        timezone = app.config.get("MONITORING_SCHEDULER_TIMEZONE", "UTC")

        with self._lock:
            if self._scheduler.running and self._scheduler.get_job(self._job_id):
                return

            try:
                trigger = CronTrigger.from_crontab(cron_expression, timezone=timezone)
            except ValueError as exc:
                self._last_error = str(exc)
                logger.exception(
                    "monitoring_scheduler_invalid_cron cron=%s timezone=%s", cron_expression, timezone
                )
                return

            if not self._scheduler.running:
                self._scheduler.start()

            self._scheduler.add_job(
                func=self._build_job(app),
                trigger=trigger,
                id=self._job_id,
                replace_existing=True,
                max_instances=1,
                coalesce=True,
                misfire_grace_time=300,
            )
            self._last_error = None
            logger.info(
                "monitoring_scheduler_started cron=%s timezone=%s next_run=%s",
                cron_expression,
                timezone,
                self.get_status().get("next_run_time"),
            )

    def run_now(self, app, initiated_by: str = "scheduler-manual") -> dict:
        with app.app_context():
            service = URLHealthCheckService()
            return service.execute_checks(trigger_type="SCHEDULED", initiated_by=initiated_by)

    def get_status(self) -> dict:
        job = self._scheduler.get_job(self._job_id)
        next_run_time = None
        if job and job.next_run_time:
            next_run_time = self._to_iso(job.next_run_time)

        return {
            "enabled": bool(job),
            "running": bool(self._scheduler.running and job),
            "next_run_time": next_run_time,
            "last_error": self._last_error,
        }

    def _build_job(self, app):
        def _job():
            try:
                result = self.run_now(app=app, initiated_by="scheduler")
                logger.info(
                    "monitoring_scheduler_execution_completed execution_id=%s status=%s",
                    result.get("id"),
                    result.get("overall_status"),
                )
            except Exception:
                logger.exception("monitoring_scheduler_execution_failed")

        return _job

    @staticmethod
    def _to_iso(value: datetime) -> str:
        return value.isoformat()


monitoring_scheduler_service = MonitoringSchedulerService()
