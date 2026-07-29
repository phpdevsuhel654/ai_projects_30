from datetime import datetime, timezone
import uuid
from time import perf_counter
import threading
import time

import requests
from flask import current_app

from app.models import CronJob, ExecutionLog
from app.repositories.cron_repository import CronRepository
from app.repositories.execution_log_repository import ExecutionLogRepository
from app.services.notification_service import NotificationService


class ExecutionService:
    _running_jobs_lock = threading.Lock()
    _running_job_ids: set[int] = set()

    @classmethod
    def _try_acquire_job_lock(cls, cron_id: int) -> bool:
        with cls._running_jobs_lock:
            if cron_id in cls._running_job_ids:
                return False
            cls._running_job_ids.add(cron_id)
            return True

    @classmethod
    def _release_job_lock(cls, cron_id: int) -> None:
        with cls._running_jobs_lock:
            cls._running_job_ids.discard(cron_id)

    @staticmethod
    def execute_single_run(
        job: CronJob,
        execution_no: int,
        bulk_execution_id: str | None = None,
    ) -> ExecutionLog:
        timeout_seconds = current_app.config["REQUEST_TIMEOUT_SECONDS"]
        retry_count = current_app.config["REQUEST_RETRY_COUNT"]
        backoff_seconds = current_app.config["REQUEST_RETRY_BACKOFF_SECONDS"]
        total_attempts = retry_count + 1

        latest_status_code = None
        latest_response_body = None
        latest_error_message = None
        latest_duration = 0.0

        for attempt in range(1, total_attempts + 1):
            start = perf_counter()
            try:
                response = requests.get(job.url, timeout=timeout_seconds)
                latest_duration = perf_counter() - start
                latest_status_code = response.status_code
                latest_response_body = response.text[:4000]
                if 200 <= response.status_code < 400:
                    return ExecutionLogRepository.create(
                        ExecutionLog(
                            cron_job_id=job.id,
                            bulk_execution_id=bulk_execution_id,
                            execution_no=execution_no,
                            status="success",
                            status_code=latest_status_code,
                            response_time=latest_duration,
                            response_body=latest_response_body,
                            error_message=None,
                            executed_at=datetime.now(timezone.utc),
                        )
                    )

                latest_error_message = (
                    f"HTTP {response.status_code} on attempt {attempt}/{total_attempts}"
                )
            except requests.RequestException as exc:
                latest_duration = perf_counter() - start
                latest_error_message = f"{exc} (attempt {attempt}/{total_attempts})"

            if attempt < total_attempts:
                sleep_for = backoff_seconds * (2 ** (attempt - 1))
                time.sleep(sleep_for)

        return ExecutionLogRepository.create(
            ExecutionLog(
                cron_job_id=job.id,
                bulk_execution_id=bulk_execution_id,
                execution_no=execution_no,
                status="failure",
                status_code=latest_status_code,
                response_time=latest_duration,
                response_body=latest_response_body,
                error_message=latest_error_message,
                executed_at=datetime.now(timezone.utc),
            )
        )

    @staticmethod
    def run_job(
        cron_id: int,
        source: str = "manual",
        bulk_execution_id: str | None = None,
    ) -> dict:
        job = CronRepository.get_by_id(cron_id)
        if not job:
            return {"error": "cron job not found"}

        if not ExecutionService._try_acquire_job_lock(cron_id):
            return {
                "error": "cron job is already running",
                "code": "JOB_ALREADY_RUNNING",
                "cron_job_id": cron_id,
            }

        logs: list[dict] = []
        try:
            for execution_no in range(1, job.execution_count + 1):
                log = ExecutionService.execute_single_run(
                    job,
                    execution_no,
                    bulk_execution_id=bulk_execution_id,
                )
                logs.append(log.to_dict())
        finally:
            ExecutionService._release_job_lock(cron_id)

        result = {
            "cron_job": job.to_dict(),
            "source": source,
            "bulk_execution_id": bulk_execution_id,
            "executions": logs,
        }
        NotificationService.notify_job_result(result)
        return result

    @staticmethod
    def run_all_active_jobs() -> dict:
        jobs = CronRepository.list_active()
        output: list[dict] = []
        bulk_execution_id = f"bulk-{uuid.uuid4().hex}"

        for job in jobs:
            output.append(
                ExecutionService.run_job(
                    job.id,
                    source="bulk",
                    bulk_execution_id=bulk_execution_id,
                )
            )

        summary = {
            "count": len(output),
            "bulk_execution_id": bulk_execution_id,
            "results": output,
        }

        # Batch-level execution summary notification.
        NotificationService.notify_run_all_summary(summary)
        return summary
