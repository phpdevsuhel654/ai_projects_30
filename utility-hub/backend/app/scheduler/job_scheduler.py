from __future__ import annotations

import re

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from flask import Flask

from app.repositories.cron_repository import CronRepository
from app.services.execution_service import ExecutionService


class JobScheduler:
    def __init__(self) -> None:
        self.scheduler = BackgroundScheduler()
        self.started = False
        self._app: Flask | None = None

    def start(self, app: Flask) -> None:
        if self.started:
            return

        timezone = app.config.get("SCHEDULER_TIMEZONE", "UTC")
        self.scheduler.configure(timezone=timezone)
        self.scheduler.start()
        self.started = True
        self._app = app
        self.sync_all_jobs()

    def _job_id(self, cron_job_id: int) -> str:
        return f"cron_job_{cron_job_id}"

    def _parse_custom_expression(self, expression: str) -> dict:
        parts = re.split(r"\s+", expression.strip())
        if len(parts) != 5:
            raise ValueError("custom schedule_expression must have 5 cron parts")

        minute, hour, day, month, day_of_week = parts
        return {
            "minute": minute,
            "hour": hour,
            "day": day,
            "month": month,
            "day_of_week": day_of_week,
        }

    def _build_trigger(self, schedule_type: str, schedule_expression: str | None) -> CronTrigger:
        if not self._app:
            raise ValueError("scheduler app context is unavailable")

        hourly_minute = str(self._app.config.get("SCHEDULER_HOURLY_MINUTE", 0))
        daily_hour = str(self._app.config.get("SCHEDULER_DAILY_HOUR", 1))
        daily_minute = str(self._app.config.get("SCHEDULER_DAILY_MINUTE", 0))

        if schedule_type == "hourly":
            return CronTrigger(minute=hourly_minute)

        if schedule_type == "daily":
            return CronTrigger(hour=daily_hour, minute=daily_minute)

        if schedule_type == "custom":
            if not schedule_expression:
                raise ValueError("schedule_expression is required for custom schedule")
            parts = self._parse_custom_expression(schedule_expression)
            return CronTrigger(**parts)

        raise ValueError("unsupported schedule_type")

    def _execute_job(self, cron_job_id: int) -> None:
        if not self._app:
            return
        with self._app.app_context():
            ExecutionService.run_job(cron_job_id, source="scheduler")

    def schedule_job(self, cron_job_id: int) -> None:
        if not self.started:
            return

        if not self._app:
            return

        with self._app.app_context():
            job = CronRepository.get_by_id(cron_job_id)
            if not job or not job.is_active:
                self.remove_job(cron_job_id)
                return

            trigger = self._build_trigger(job.schedule_type, job.schedule_expression)
            self.scheduler.add_job(
                func=self._execute_job,
                trigger=trigger,
                id=self._job_id(job.id),
                replace_existing=True,
                kwargs={"cron_job_id": job.id},
                coalesce=True,
                max_instances=1,
            )

    def remove_job(self, cron_job_id: int) -> None:
        if not self.started:
            return
        job_id = self._job_id(cron_job_id)
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)

    def sync_all_jobs(self) -> None:
        if not self.started:
            return

        if not self._app:
            return

        with self._app.app_context():
            active_ids = set()
            for cron_job in CronRepository.list_active():
                active_ids.add(self._job_id(cron_job.id))
                self.schedule_job(cron_job.id)

            for scheduled_job in self.scheduler.get_jobs():
                if scheduled_job.id.startswith("cron_job_") and scheduled_job.id not in active_ids:
                    self.scheduler.remove_job(scheduled_job.id)

    def shutdown(self) -> None:
        if self.started:
            self.scheduler.shutdown()
            self.started = False
            self._app = None


job_scheduler = JobScheduler()
