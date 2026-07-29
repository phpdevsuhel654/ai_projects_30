import csv
from io import StringIO

from flask import Blueprint, Response, jsonify, request

from app.repositories.cron_repository import CronRepository
from app.repositories.execution_log_repository import ExecutionLogRepository
from app.reports.report_service import ReportService
from app.services.execution_service import ExecutionService
from app.utils.security import enforce_api_auth

execution_bp = Blueprint("execution", __name__)


@execution_bp.before_request
def _auth_guard():
    return enforce_api_auth()


@execution_bp.post("/run/<int:cron_id>")
def run_one(cron_id: int):
    result = ExecutionService.run_job(cron_id)
    if "error" in result:
        if result.get("code") == "JOB_ALREADY_RUNNING":
            return jsonify(result), 409
        return jsonify(result), 404
    return jsonify(result), 200


@execution_bp.post("/run-all")
def run_all():
    return jsonify(ExecutionService.run_all_active_jobs()), 200


@execution_bp.get("/history")
def history():
    limit = int(request.args.get("limit", 100))
    logs = ExecutionLogRepository.list_recent(limit=limit)
    return jsonify([log.to_dict() for log in logs]), 200


@execution_bp.get("/dashboard")
def dashboard():
    payload = ExecutionLogRepository.aggregate_counts()
    payload["total_urls"] = len(CronRepository.list_active())

    total_exec = payload["total_executions"]
    success = payload["success_count"]
    payload["success_percentage"] = (success / total_exec * 100) if total_exec else 0

    return jsonify(payload), 200


@execution_bp.get("/report")
def report():
    period = (request.args.get("period") or "daily").strip().lower()
    if period not in {"daily", "weekly", "monthly"}:
        return jsonify({"error": "period must be one of: daily, weekly, monthly"}), 400

    cron_job_id_raw = (request.args.get("cron_job_id") or "").strip()
    cron_job_id = int(cron_job_id_raw) if cron_job_id_raw else None
    start_at = (request.args.get("start_at") or "").strip() or None
    end_at = (request.args.get("end_at") or "").strip() or None

    return (
        jsonify(
            ReportService.summary(
                period=period,
                cron_job_id=cron_job_id,
                start_at=start_at,
                end_at=end_at,
            )
        ),
        200,
    )


@execution_bp.get("/report/trend")
def report_trend():
    days_raw = (request.args.get("days") or "7").strip()
    cron_job_id_raw = (request.args.get("cron_job_id") or "").strip()

    try:
        days = int(days_raw)
    except ValueError:
        return jsonify({"error": "days must be an integer"}), 400

    cron_job_id = int(cron_job_id_raw) if cron_job_id_raw else None

    return jsonify(ReportService.trend(days=days, cron_job_id=cron_job_id)), 200


@execution_bp.get("/report/errors")
def report_errors():
    period = (request.args.get("period") or "daily").strip().lower()
    if period not in {"daily", "weekly", "monthly"}:
        return jsonify({"error": "period must be one of: daily, weekly, monthly"}), 400

    limit_raw = (request.args.get("limit") or "10").strip()
    cron_job_id_raw = (request.args.get("cron_job_id") or "").strip()
    start_at = (request.args.get("start_at") or "").strip() or None
    end_at = (request.args.get("end_at") or "").strip() or None

    try:
        limit = int(limit_raw)
    except ValueError:
        return jsonify({"error": "limit must be an integer"}), 400

    cron_job_id = int(cron_job_id_raw) if cron_job_id_raw else None

    return (
        jsonify(
            ReportService.error_summary(
                period=period,
                cron_job_id=cron_job_id,
                start_at=start_at,
                end_at=end_at,
                limit=limit,
            )
        ),
        200,
    )


@execution_bp.get("/report/export")
def report_export():
    period = (request.args.get("period") or "daily").strip().lower()
    if period not in {"daily", "weekly", "monthly"}:
        return jsonify({"error": "period must be one of: daily, weekly, monthly"}), 400

    cron_job_id_raw = (request.args.get("cron_job_id") or "").strip()
    cron_job_id = int(cron_job_id_raw) if cron_job_id_raw else None
    start_at = (request.args.get("start_at") or "").strip() or None
    end_at = (request.args.get("end_at") or "").strip() or None

    report_data = ReportService.summary(
        period=period,
        cron_job_id=cron_job_id,
        start_at=start_at,
        end_at=end_at,
    )

    csv_buffer = StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerow(
        [
            "cron_job_id",
            "name",
            "url",
            "run_count",
            "success_count",
            "failure_count",
            "avg_response_time",
        ]
    )
    for item in report_data["items"]:
        writer.writerow(
            [
                item["cron_job_id"],
                item["name"],
                item["url"],
                item["run_count"],
                item["success_count"],
                item["failure_count"],
                f"{item['avg_response_time']:.6f}",
            ]
        )

    filename = f"cron_report_{period}.csv"
    return Response(
        csv_buffer.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
