from __future__ import annotations

from datetime import datetime, timezone

import requests
from flask import current_app


class NotificationService:
    @staticmethod
    def _is_enabled() -> bool:
        return bool(current_app.config.get("NOTIFICATIONS_ENABLED", False))

    @staticmethod
    def _send_payload(payload: dict) -> None:
        if not NotificationService._is_enabled():
            return

        webhook_url = current_app.config.get("NOTIFICATION_WEBHOOK_URL", "")
        timeout = current_app.config.get("NOTIFICATION_TIMEOUT_SECONDS", 5)

        current_app.logger.info("notification_payload=%s", payload)

        if not webhook_url:
            return

        try:
            requests.post(webhook_url, json=payload, timeout=timeout)
        except requests.RequestException as exc:
            current_app.logger.warning("notification delivery failed: %s", exc)

    @staticmethod
    def notify_job_result(result: dict) -> None:
        if "executions" not in result:
            return

        executions = result.get("executions", [])
        total = len(executions)
        failed_items = [item for item in executions if item.get("status") == "failure"]
        failed = len(failed_items)
        succeeded = total - failed

        if failed == 0 and not current_app.config.get("NOTIFY_ON_SUMMARY", True):
            return

        if failed > 0 and not current_app.config.get("NOTIFY_ON_FAILURE", True):
            return

        payload = {
            "type": "cron_job_execution",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "cron_job": result.get("cron_job", {}),
            "source": result.get("source"),
            "summary": {
                "total": total,
                "success": succeeded,
                "failure": failed,
            },
            "failed_executions": failed_items,
        }
        NotificationService._send_payload(payload)

    @staticmethod
    def notify_run_all_summary(result: dict) -> None:
        if not current_app.config.get("NOTIFY_ON_SUMMARY", True):
            return

        total_jobs = result.get("count", 0)
        total_runs = 0
        success_count = 0
        failure_count = 0
        failed_jobs = []

        for item in result.get("results", []):
            executions = item.get("executions", [])
            total_runs += len(executions)
            failures = [entry for entry in executions if entry.get("status") == "failure"]
            failure_count += len(failures)
            success_count += len(executions) - len(failures)
            if failures:
                failed_jobs.append(
                    {
                        "cron_job": item.get("cron_job", {}),
                        "failures": len(failures),
                    }
                )

        payload = {
            "type": "run_all_summary",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "jobs": total_jobs,
                "runs": total_runs,
                "success": success_count,
                "failure": failure_count,
            },
            "failed_jobs": failed_jobs,
        }
        NotificationService._send_payload(payload)
