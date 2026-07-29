from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request

from app.services.monitoring_scheduler_service import monitoring_scheduler_service
from app.services.url_health_check_service import URLHealthCheckService
from app.utils.security import enforce_api_auth


monitoring_bp = Blueprint("monitoring_api", __name__, url_prefix="/api/monitoring")
service = URLHealthCheckService()


@monitoring_bp.before_request
def _auth_guard():
    return enforce_api_auth()


@monitoring_bp.post("/urls")
def add_url():
    payload = request.get_json(silent=True) or {}
    try:
        result = service.add_url(payload)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(result), 201


@monitoring_bp.get("/urls")
def list_urls():
    active_only_arg = (request.args.get("active_only") or "false").strip().lower()
    active_only = active_only_arg in {"1", "true", "yes"}
    return jsonify({"items": service.list_urls(active_only=active_only)}), 200


@monitoring_bp.put("/urls/<int:url_id>")
def update_url(url_id: int):
    payload = request.get_json(silent=True) or {}
    try:
        result = service.update_url(url_id, payload)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except LookupError as exc:
        return jsonify({"error": str(exc)}), 404
    return jsonify(result), 200


@monitoring_bp.delete("/urls/<int:url_id>")
def delete_url(url_id: int):
    deleted = service.delete_url(url_id)
    if not deleted:
        return jsonify({"error": "URL record not found"}), 404
    return jsonify({"deleted": True, "id": url_id}), 200


@monitoring_bp.post("/execute")
def execute_checks():
    payload = request.get_json(silent=True) or {}
    trigger_type = payload.get("trigger_type", "MANUAL")
    initiated_by = payload.get("initiated_by")

    result = service.execute_checks(trigger_type=trigger_type, initiated_by=initiated_by)
    return jsonify(result), 200


@monitoring_bp.get("/reports")
def reports():
    limit_arg = request.args.get("limit", "20")
    try:
        limit = int(limit_arg)
    except ValueError:
        return jsonify({"error": "limit must be an integer"}), 400

    return jsonify({"items": service.list_history(limit=limit)}), 200


@monitoring_bp.get("/reports/<int:execution_id>")
def report_detail(execution_id: int):
    try:
        result = service.get_report(execution_id)
    except LookupError as exc:
        return jsonify({"error": str(exc)}), 404
    return jsonify(result), 200


@monitoring_bp.get("/scheduler/status")
def scheduler_status():
    status = monitoring_scheduler_service.get_status()
    status.update(
        {
            "cron": current_app.config.get("MONITORING_SCHEDULER_CRON"),
            "timezone": current_app.config.get("MONITORING_SCHEDULER_TIMEZONE"),
            "configured": bool(current_app.config.get("MONITORING_SCHEDULER_ENABLED", False)),
        }
    )
    return jsonify(status), 200


@monitoring_bp.post("/scheduler/run-now")
def scheduler_run_now():
    payload = request.get_json(silent=True) or {}
    initiated_by = (payload.get("initiated_by") or "scheduler-api").strip() or "scheduler-api"
    result = monitoring_scheduler_service.run_now(app=current_app, initiated_by=initiated_by)
    return jsonify(result), 200
