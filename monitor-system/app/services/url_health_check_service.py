from __future__ import annotations

import logging
import socket
import time
from datetime import datetime, timezone
from urllib.parse import urlparse

import requests

from app.repositories.url_monitoring_repository import URLMonitoringRepository


logger = logging.getLogger(__name__)


class URLHealthCheckService:
    def __init__(self, repository: URLMonitoringRepository | None = None):
        self.repository = repository or URLMonitoringRepository()

    def add_url(self, payload: dict) -> dict:
        url = self._normalize_url(payload.get("url", ""))
        notes = (payload.get("notes") or "").strip() or None
        is_active = bool(payload.get("is_active", True))

        if self.repository.get_by_url(url):
            raise ValueError("URL already exists")

        row = self.repository.add_url(url=url, notes=notes, is_active=is_active)
        logger.info("monitoring_url_added id=%s url=%s is_active=%s", row.id, row.url, row.is_active)
        return self._url_to_dict(row)

    def update_url(self, url_id: int, payload: dict) -> dict:
        url = payload.get("url")
        notes = payload.get("notes")
        is_active = payload.get("is_active")

        if url is not None:
            url = self._normalize_url(url)
            existing = self.repository.get_by_url(url)
            if existing and existing.id != url_id:
                raise ValueError("URL already exists")

        row = self.repository.update_url(url_id=url_id, url=url, notes=notes, is_active=is_active)
        if row is None:
            raise LookupError("URL record not found")
        logger.info("monitoring_url_updated id=%s url=%s is_active=%s", row.id, row.url, row.is_active)
        return self._url_to_dict(row)

    def delete_url(self, url_id: int) -> bool:
        deleted = self.repository.delete_url(url_id)
        logger.info("monitoring_url_deleted id=%s deleted=%s", url_id, deleted)
        return deleted

    def list_urls(self, active_only: bool = False) -> list[dict]:
        return [self._url_to_dict(row) for row in self.repository.list_urls(active_only=active_only)]

    def execute_checks(self, trigger_type: str = "MANUAL", initiated_by: str | None = None) -> dict:
        urls = self.repository.list_urls(active_only=True)
        logger.info("monitoring_execution_started trigger=%s initiated_by=%s total_active_urls=%s", trigger_type, initiated_by, len(urls))
        started_at = datetime.now(timezone.utc)
        started_counter = time.perf_counter()

        detail_rows = []
        success_count = 0
        failed_count = 0

        for row in urls:
            check = self._check_single_url(row.url)
            detail_rows.append(
                {
                    "monitored_url_id": row.id,
                    "dns_resolved": check["dns_resolved"],
                    "http_status_code": check["http_status_code"],
                    "https_valid": check["https_valid"],
                    "response_time_ms": check["response_time_ms"],
                    "availability_status": check["availability_status"],
                    "error_message": check["error_message"],
                    "checked_at": datetime.now(timezone.utc),
                }
            )
            if check["availability_status"] == "UP":
                success_count += 1
            else:
                failed_count += 1

        ended_at = datetime.now(timezone.utc)
        total_duration_ms = int((time.perf_counter() - started_counter) * 1000)

        if failed_count == 0:
            overall_status = "SUCCESS"
        elif success_count == 0:
            overall_status = "FAILED"
        else:
            overall_status = "PARTIAL"

        history = self.repository.create_execution(
            trigger_type=trigger_type,
            started_at=started_at,
            ended_at=ended_at,
            total_duration_ms=total_duration_ms,
            total_urls=len(urls),
            success_count=success_count,
            failed_count=failed_count,
            overall_status=overall_status,
            initiated_by=initiated_by,
            details=detail_rows,
        )

        logger.info(
            "monitoring_execution_completed id=%s status=%s success=%s failed=%s duration_ms=%s",
            history.id,
            overall_status,
            success_count,
            failed_count,
            total_duration_ms,
        )

        return self._history_to_dict(history, include_details=True)

    def list_history(self, limit: int = 20) -> list[dict]:
        return [self._history_to_dict(row, include_details=False) for row in self.repository.list_execution_history(limit=limit)]

    def get_report(self, execution_id: int) -> dict:
        row = self.repository.get_execution(execution_id)
        if row is None:
            raise LookupError("Execution record not found")
        return self._history_to_dict(row, include_details=True)

    def _check_single_url(self, url: str) -> dict:
        parsed = urlparse(url)
        hostname = parsed.hostname
        if not hostname:
            return {
                "dns_resolved": False,
                "http_status_code": None,
                "https_valid": False,
                "response_time_ms": None,
                "availability_status": "DOWN",
                "error_message": "Invalid hostname",
            }

        dns_resolved = True
        error_message = None

        try:
            socket.getaddrinfo(hostname, parsed.port or (443 if parsed.scheme == "https" else 80))
        except socket.gaierror as exc:
            dns_resolved = False
            error_message = f"DNS resolution failed: {exc}"

        http_status_code = None
        response_time_ms = None
        https_valid = parsed.scheme.lower() == "http"

        if dns_resolved:
            started = time.perf_counter()
            try:
                response = requests.get(url, timeout=10, allow_redirects=True)
                response_time_ms = int((time.perf_counter() - started) * 1000)
                http_status_code = int(response.status_code)
            except requests.RequestException as exc:
                response_time_ms = int((time.perf_counter() - started) * 1000)
                error_message = str(exc)

        if dns_resolved and parsed.scheme.lower() == "https":
            try:
                requests.get(url, timeout=10, verify=True)
                https_valid = True
            except requests.exceptions.SSLError as exc:
                https_valid = False
                error_message = f"SSL validation failed: {exc}"
            except requests.RequestException:
                https_valid = False

        is_up = dns_resolved and http_status_code is not None and 200 <= http_status_code < 400 and https_valid

        return {
            "dns_resolved": dns_resolved,
            "http_status_code": http_status_code,
            "https_valid": https_valid,
            "response_time_ms": response_time_ms,
            "availability_status": "UP" if is_up else "DOWN",
            "error_message": error_message,
        }

    def _normalize_url(self, raw_url: str) -> str:
        if not isinstance(raw_url, str) or not raw_url.strip():
            raise ValueError("url is required")

        cleaned = raw_url.strip()
        parsed = urlparse(cleaned)

        if parsed.scheme.lower() not in {"http", "https"}:
            raise ValueError("url must start with http:// or https://")
        if not parsed.netloc:
            raise ValueError("url must include a valid host")
        return cleaned

    def _url_to_dict(self, row) -> dict:
        return {
            "id": row.id,
            "url": row.url,
            "is_active": row.is_active,
            "notes": row.notes,
            "created_at": row.created_at.isoformat(),
            "updated_at": row.updated_at.isoformat(),
        }

    def _history_to_dict(self, row, include_details: bool) -> dict:
        data = {
            "id": row.id,
            "trigger_type": row.trigger_type,
            "execution_start_time": row.started_at.isoformat(),
            "execution_end_time": row.ended_at.isoformat(),
            "total_duration_ms": row.total_duration_ms,
            "total_urls": row.total_urls,
            "active_urls": row.total_urls,
            "failed_urls": row.failed_count,
            "success_urls": row.success_count,
            "overall_status": row.overall_status,
            "initiated_by": row.initiated_by,
            "last_execution_time": row.ended_at.isoformat(),
        }

        if include_details:
            data["execution_details"] = [
                {
                    "url": detail.monitored_url.url,
                    "status": detail.availability_status,
                    "http_status_code": detail.http_status_code,
                    "response_time_ms": detail.response_time_ms,
                    "dns_resolved": detail.dns_resolved,
                    "https_valid": detail.https_valid,
                    "error_message": detail.error_message,
                    "checked_at": detail.checked_at.isoformat(),
                }
                for detail in row.details
            ]
        return data
