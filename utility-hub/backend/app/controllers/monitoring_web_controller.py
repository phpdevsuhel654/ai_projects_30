from __future__ import annotations

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for

from app.services.monitoring_scheduler_service import monitoring_scheduler_service
from app.services.url_health_check_service import URLHealthCheckService
from app.utils.security import web_login_required


monitoring_web_bp = Blueprint("monitoring_web", __name__)
service = URLHealthCheckService()


@monitoring_web_bp.get("/url-monitoring")
@web_login_required
def monitoring_dashboard():
    urls = service.list_urls(active_only=False)
    history = service.list_history(limit=10)
    latest = history[0] if history else None

    cards = {
        "total_urls": len(urls),
        "active_urls": sum(1 for row in urls if row["is_active"]),
        "failed_urls": (latest or {}).get("failed_urls", 0),
        "last_execution_time": (latest or {}).get("last_execution_time"),
    }

    latest_report = None
    if latest:
        try:
            latest_report = service.get_report(latest["id"])
        except LookupError:
            latest_report = None

    scheduler_status = monitoring_scheduler_service.get_status()
    scheduler_status.update(
        {
            "configured": bool(current_app.config.get("MONITORING_SCHEDULER_ENABLED", False)),
            "cron": current_app.config.get("MONITORING_SCHEDULER_CRON"),
            "timezone": current_app.config.get("MONITORING_SCHEDULER_TIMEZONE"),
        }
    )

    return render_template(
        "monitoring_dashboard.html",
        urls=urls,
        history=history,
        cards=cards,
        latest_report=latest_report,
        scheduler_status=scheduler_status,
    )


@monitoring_web_bp.post("/url-monitoring/add")
@web_login_required
def add_url_ui():
    payload = {
        "url": request.form.get("url", "").strip(),
        "notes": request.form.get("notes", "").strip(),
        "is_active": request.form.get("is_active") == "on",
    }

    try:
        service.add_url(payload)
        flash("URL added successfully.", "success")
    except ValueError as exc:
        flash(str(exc), "danger")

    return redirect(url_for("monitoring_web.monitoring_dashboard"))


@monitoring_web_bp.post("/url-monitoring/<int:url_id>/update")
@web_login_required
def update_url_ui(url_id: int):
    payload = {
        "url": request.form.get("url", "").strip(),
        "notes": request.form.get("notes", "").strip(),
        "is_active": request.form.get("is_active") == "on",
    }

    try:
        service.update_url(url_id, payload)
        flash("URL updated successfully.", "success")
    except (ValueError, LookupError) as exc:
        flash(str(exc), "danger")

    return redirect(url_for("monitoring_web.monitoring_dashboard"))


@monitoring_web_bp.post("/url-monitoring/<int:url_id>/delete")
@web_login_required
def delete_url_ui(url_id: int):
    deleted = service.delete_url(url_id)
    if deleted:
        flash("URL deleted successfully.", "success")
    else:
        flash("URL record not found.", "danger")
    return redirect(url_for("monitoring_web.monitoring_dashboard"))


@monitoring_web_bp.post("/url-monitoring/execute")
@web_login_required
def execute_checks_ui():
    initiated_by = request.form.get("initiated_by", "web-ui").strip() or "web-ui"
    service.execute_checks(trigger_type="MANUAL", initiated_by=initiated_by)
    flash("Health check execution completed.", "success")
    return redirect(url_for("monitoring_web.monitoring_dashboard"))
