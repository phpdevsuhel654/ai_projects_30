from flask import Blueprint, jsonify, request

from app.services.cron_service import CronService
from app.utils.security import enforce_api_auth
from app.utils.validators import validate_schedule

cron_bp = Blueprint("cron", __name__)


@cron_bp.before_request
def _auth_guard():
    return enforce_api_auth()


@cron_bp.post("/cron")
def create_cron_job():
    data = request.get_json(silent=True) or {}

    name = data.get("name", "").strip()
    url = data.get("url", "").strip()
    execution_count = int(data.get("execution_count", 1) or 1)
    schedule_type = (data.get("schedule_type") or "daily").strip().lower()
    schedule_expression = (data.get("schedule_expression") or "").strip() or None

    if not name or not url:
        return jsonify({"error": "name and url are required"}), 400

    if execution_count < 1:
        return jsonify({"error": "execution_count must be >= 1"}), 400

    schedule_error = validate_schedule(schedule_type, schedule_expression)
    if schedule_error:
        return jsonify({"error": schedule_error}), 400

    cron_job = CronService.create(
        {
            "name": name,
            "url": url,
            "execution_count": execution_count,
            "schedule_type": schedule_type,
            "schedule_expression": schedule_expression,
            "is_active": bool(data.get("is_active", True)),
            "description": (data.get("description") or "").strip() or None,
        }
    )

    return jsonify(cron_job.to_dict()), 201


@cron_bp.get("/cron")
def list_cron_jobs():
    items = CronService.list_all()
    return jsonify([item.to_dict() for item in items]), 200


@cron_bp.get("/cron/<int:cron_id>")
def get_cron_job(cron_id: int):
    item = CronService.get(cron_id)
    if not item:
        return jsonify({"error": "cron job not found"}), 404
    return jsonify(item.to_dict()), 200


@cron_bp.put("/cron/<int:cron_id>")
def update_cron_job(cron_id: int):
    data = request.get_json(silent=True) or {}

    payload = {}

    if "name" in data:
        payload["name"] = str(data["name"]).strip()
    if "url" in data:
        payload["url"] = str(data["url"]).strip()
    if "execution_count" in data:
        execution_count = int(data["execution_count"])
        if execution_count < 1:
            return jsonify({"error": "execution_count must be >= 1"}), 400
        payload["execution_count"] = execution_count
    if "schedule_type" in data:
        payload["schedule_type"] = str(data["schedule_type"]).strip().lower()
    if "schedule_expression" in data:
        payload["schedule_expression"] = (
            str(data["schedule_expression"]).strip() or None
        )
    if "is_active" in data:
        payload["is_active"] = bool(data["is_active"])
    if "description" in data:
        payload["description"] = str(data["description"]).strip() or None

    current = CronService.get(cron_id)
    if not current:
        return jsonify({"error": "cron job not found"}), 404

    effective_schedule_type = payload.get("schedule_type", current.schedule_type)
    effective_schedule_expression = payload.get(
        "schedule_expression", current.schedule_expression
    )
    schedule_error = validate_schedule(
        effective_schedule_type,
        effective_schedule_expression,
    )
    if schedule_error:
        return jsonify({"error": schedule_error}), 400

    item = CronService.update(cron_id, payload)
    if not item:
        return jsonify({"error": "cron job not found"}), 404

    return jsonify(item.to_dict()), 200


@cron_bp.delete("/cron/<int:cron_id>")
def delete_cron_job(cron_id: int):
    deleted = CronService.delete(cron_id)
    if not deleted:
        return jsonify({"error": "cron job not found"}), 404
    return jsonify({"message": "deleted"}), 200
