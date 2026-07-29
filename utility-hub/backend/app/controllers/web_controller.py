import secrets
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for

from app.repositories.execution_log_repository import ExecutionLogRepository
from app.reports.report_service import ReportService
from app.services.cron_service import CronService
from app.services.execution_service import ExecutionService
from app.utils.security import web_login_required
from app.utils.validators import validate_schedule
from app.models.address_validation import AddressValidation
from app.models.url_monitoring import MonitoredURL

web_bp = Blueprint("web", __name__)

HISTORY_CLEANUP_OPTIONS = {
    "15d": {"label": "Archive 15 days old records", "delta": timedelta(days=15)},
    "1m": {"label": "Archive 1 month old record", "delta": timedelta(days=30)},
    "3m": {"label": "Archive 3 months old records", "delta": timedelta(days=90)},
    "6m": {"label": "Archive 6 months old records", "delta": timedelta(days=180)},
}
DEFAULT_HISTORY_CLEANUP_OPTION = "1m"


def _parse_datetime_input(value: str | None) -> datetime | None:
    if not value:
        return None
    raw = value.strip()
    if not raw:
        return None

    parsed = datetime.fromisoformat(raw)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _to_datetime_local_value(value: datetime | None) -> str:
    if value is None:
        return ""
    if value.tzinfo is not None:
        value = value.astimezone(timezone.utc).replace(tzinfo=None)
    return value.strftime("%Y-%m-%dT%H:%M")


@web_bp.before_request
def _web_auth_guard():
    if not current_app.config.get("WEB_AUTH_ENABLED", False):
        return None

    if request.endpoint in {"web.login_page", "web.login_submit", "static"}:
        return None

    if session.get("web_user_authenticated"):
        return None

    return redirect(url_for("web.login_page", next=request.path))


@web_bp.get("/login")
def login_page():
    if not current_app.config.get("WEB_AUTH_ENABLED", False):
        return redirect(url_for("web.dashboard_page"))
    return render_template("login.html")


@web_bp.post("/login")
def login_submit():
    if not current_app.config.get("WEB_AUTH_ENABLED", False):
        return redirect(url_for("web.dashboard_page"))

    username = (request.form.get("username") or "").strip()
    password = (request.form.get("password") or "").strip()

    valid_username = current_app.config.get("WEB_AUTH_USERNAME", "")
    valid_password = current_app.config.get("WEB_AUTH_PASSWORD", "")

    if secrets.compare_digest(username, valid_username) and secrets.compare_digest(
        password, valid_password
    ):
        session["web_user_authenticated"] = True
        next_url = (request.args.get("next") or "").strip() or url_for("web.dashboard_page")
        return redirect(next_url)

    flash("Invalid credentials.", "danger")
    return redirect(url_for("web.login_page"))


@web_bp.post("/logout")
def logout():
    session.pop("web_user_authenticated", None)
    return redirect(url_for("web.login_page"))


@web_bp.get("/")
@web_login_required
def index():
    return redirect(url_for("web.dashboard_page"))


@web_bp.get("/dashboard")
@web_login_required
def dashboard_page():
    stats = ExecutionLogRepository.aggregate_counts()
    cron_jobs = CronService.list_all()
    total_exec = stats["total_executions"]
    stats["total_urls"] = len(cron_jobs)
    stats["active_urls"] = len([job for job in cron_jobs if job.is_active])
    stats["success_percentage"] = (
        (stats["success_count"] / total_exec) * 100 if total_exec else 0
    )
    stats["address_validations"] = AddressValidation.query.count()
    stats["monitored_urls"] = MonitoredURL.query.count()

    recent_logs = [log.to_dict() for log in ExecutionLogRepository.list_recent(limit=10)]

    return render_template(
        "dashboard.html",
        stats=stats,
        recent_logs=recent_logs,
    )


@web_bp.route("/cron-jobs", methods=["GET", "POST"])
@web_login_required
def cron_jobs_page():
    if request.method == "POST":
        form = request.form
        form_mode = (form.get("form_mode") or "create").strip().lower()
        cron_id_raw = (form.get("cron_id") or "").strip()

        execution_count_raw = (form.get("execution_count") or "1").strip()
        try:
            execution_count = int(execution_count_raw)
        except ValueError:
            flash("Execution count must be a valid integer.", "danger")
            return redirect(url_for("web.cron_jobs_page"))

        payload = {
            "name": (form.get("name") or "").strip(),
            "url": (form.get("url") or "").strip(),
            "execution_count": execution_count,
            "schedule_type": (form.get("schedule_type") or "daily").strip().lower(),
            "schedule_expression": (form.get("schedule_expression") or "").strip() or None,
            "is_active": form.get("is_active") == "on",
            "description": (form.get("description") or "").strip() or None,
        }

        if not payload["name"] or not payload["url"]:
            flash("Name and URL are required.", "danger")
            return redirect(url_for("web.cron_jobs_page"))

        if payload["execution_count"] < 1:
            flash("Execution count must be >= 1.", "danger")
            return redirect(url_for("web.cron_jobs_page"))

        schedule_error = validate_schedule(
            payload["schedule_type"],
            payload["schedule_expression"],
        )
        if schedule_error:
            flash(schedule_error, "danger")
            return redirect(url_for("web.cron_jobs_page"))

        if form_mode == "edit":
            try:
                cron_id = int(cron_id_raw)
            except ValueError:
                flash("Invalid cron job ID.", "danger")
                return redirect(url_for("web.cron_jobs_page"))

            updated = CronService.update(cron_id, payload)
            if not updated:
                flash("Cron job not found.", "danger")
                return redirect(url_for("web.cron_jobs_page"))

            flash("Cron job updated successfully.", "success")
        else:
            CronService.create(payload)
            flash("Cron job added successfully.", "success")

        return redirect(url_for("web.cron_jobs_page"))

    edit_id_raw = (request.args.get("edit_id") or "").strip()
    edit_job = None
    if edit_id_raw:
        try:
            edit_id = int(edit_id_raw)
            target = CronService.get(edit_id)
            if target:
                edit_job = target.to_dict()
        except ValueError:
            edit_job = None

    jobs = [job.to_dict() for job in CronService.list_all()]
    return render_template(
        "cron_jobs.html",
        jobs=jobs,
        edit_job=edit_job,
        form_mode="edit" if edit_job else "create",
    )


@web_bp.post("/cron-jobs/<int:cron_id>/toggle")
@web_login_required
def cron_job_toggle(cron_id: int):
    job = CronService.get(cron_id)
    if not job:
        flash("Cron job not found.", "danger")
        return redirect(url_for("web.cron_jobs_page"))

    CronService.update(
        cron_id,
        {
            "is_active": not job.is_active,
        },
    )
    flash("Cron job status updated.", "success")
    return redirect(url_for("web.cron_jobs_page"))


@web_bp.post("/cron-jobs/<int:cron_id>/run")
@web_login_required
def cron_job_run(cron_id: int):
    result = ExecutionService.run_job(cron_id)
    if "error" in result:
        flash(result["error"], "danger")
    else:
        flash("Cron job execution completed.", "success")
    return redirect(url_for("web.cron_jobs_page"))


@web_bp.post("/cron-jobs/<int:cron_id>/delete")
@web_login_required
def cron_job_delete(cron_id: int):
    if not CronService.delete(cron_id):
        flash("Cron job not found.", "danger")
    else:
        flash("Cron job deleted.", "success")
    return redirect(url_for("web.cron_jobs_page"))


@web_bp.post("/run-all")
@web_login_required
def run_all_page():
    result = ExecutionService.run_all_active_jobs()
    flash(f"Triggered {result.get('count', 0)} active cron job(s).", "success")
    return redirect(url_for("web.dashboard_page"))


@web_bp.post("/backup-database")
@web_login_required
def backup_database():
    try:
        from app.config.settings import Config
        
        db_uri = current_app.config.get("SQLALCHEMY_DATABASE_URI", "")
        
        if not db_uri.startswith("sqlite:"):
            flash("Database backup is only supported for SQLite databases.", "danger")
            return redirect(url_for("web.dashboard_page"))
        
        # Get the database path from config
        base_dir = Path(current_app.config.get("BASE_DIR", Path(__file__).resolve().parents[2]))
        db_path = base_dir / "database" / "cron_monitor.db"
        
        if not db_path.exists():
            flash(f"Database file not found at {db_path}.", "danger")
            return redirect(url_for("web.dashboard_page"))
        
        backup_dir = db_path.parent / "backups"
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"cron_monitor_backup_{timestamp}.db"
        
        shutil.copy2(db_path, backup_path)
        
        flash(f"Database backed up successfully to {backup_path.name}.", "success")
    except Exception as e:
        flash(f"Database backup failed: {str(e)}", "danger")
    
    return redirect(url_for("web.dashboard_page"))


@web_bp.get("/history")
@web_login_required
def history_page():
    limit_raw = (request.args.get("limit") or "100").strip()
    try:
        limit = int(limit_raw)
    except ValueError:
        limit = 100
    limit = max(1, min(limit, 500))

    cron_job_id_raw = (request.args.get("cron_job_id") or "").strip()
    bulk_execution_id = (request.args.get("bulk_execution_id") or "").strip() or None
    status = (request.args.get("status") or "").strip().lower() or None
    start_at_raw = (request.args.get("start_at") or "").strip()
    end_at_raw = (request.args.get("end_at") or "").strip()

    try:
        cron_job_id = int(cron_job_id_raw) if cron_job_id_raw else None
    except ValueError:
        cron_job_id = None

    now_utc = datetime.now(timezone.utc)
    default_start = now_utc - timedelta(days=7)
    start_at = _parse_datetime_input(start_at_raw) or default_start
    end_at = _parse_datetime_input(end_at_raw) or now_utc

    if end_at < start_at:
        start_at, end_at = end_at, start_at

    if status not in {None, "success", "failure"}:
        status = None

    logs = [
        log.to_dict()
        for log in ExecutionLogRepository.search(
            limit=limit,
            cron_job_id=cron_job_id,
            bulk_execution_id=bulk_execution_id,
            status=status,
            start_at=start_at,
            end_at=end_at,
        )
    ]
    return render_template(
        "history.html",
        logs=logs,
        selected_limit=limit,
        jobs=[job.to_dict() for job in CronService.list_all()],
        selected_cron_job_id=cron_job_id,
        selected_bulk_execution_id=bulk_execution_id,
        selected_status=status,
        selected_start_at_local=_to_datetime_local_value(start_at),
        selected_end_at_local=_to_datetime_local_value(end_at),
    )


@web_bp.get("/history-cleanup")
@web_login_required
def history_cleanup_page():
    retention = (request.args.get("retention") or DEFAULT_HISTORY_CLEANUP_OPTION).strip().lower()
    if retention not in HISTORY_CLEANUP_OPTIONS:
        retention = DEFAULT_HISTORY_CLEANUP_OPTION

    return render_template(
        "history_cleanup.html",
        cleanup_options=HISTORY_CLEANUP_OPTIONS,
        selected_retention=retention,
        default_retention=DEFAULT_HISTORY_CLEANUP_OPTION,
    )


@web_bp.post("/history-cleanup")
@web_login_required
def history_cleanup_run():
    retention = (request.form.get("retention") or DEFAULT_HISTORY_CLEANUP_OPTION).strip().lower()
    if retention not in HISTORY_CLEANUP_OPTIONS:
        flash("Invalid cleanup option selected.", "danger")
        return redirect(url_for("web.history_cleanup_page"))

    selected_option = HISTORY_CLEANUP_OPTIONS[retention]
    cutoff = datetime.now(timezone.utc) - selected_option["delta"]
    archived_count = ExecutionLogRepository.archive_executed_before(cutoff)

    flash(f"Archived {archived_count} old execution history record(s).", "success")
    return redirect(url_for("web.history_cleanup_page", retention=retention))


@web_bp.get("/reports")
@web_login_required
def reports_page():
    period = (request.args.get("period") or "daily").strip().lower()
    if period not in {"daily", "weekly", "monthly"}:
        period = "daily"

    cron_job_id_raw = (request.args.get("cron_job_id") or "").strip()
    start_at_raw = (request.args.get("start_at") or "").strip()
    end_at_raw = (request.args.get("end_at") or "").strip()
    trend_days_raw = (request.args.get("trend_days") or "7").strip()

    try:
        cron_job_id = int(cron_job_id_raw) if cron_job_id_raw else None
    except ValueError:
        cron_job_id = None

    try:
        trend_days = int(trend_days_raw)
    except ValueError:
        trend_days = 7

    start_at_dt = _parse_datetime_input(start_at_raw)
    end_at_dt = _parse_datetime_input(end_at_raw)
    if period == "daily":
        now_utc = datetime.now(timezone.utc)
        start_at_dt = start_at_dt or (now_utc - timedelta(days=7))
        end_at_dt = end_at_dt or now_utc

    if start_at_dt and end_at_dt and end_at_dt < start_at_dt:
        start_at_dt, end_at_dt = end_at_dt, start_at_dt

    start_at = start_at_dt.isoformat() if start_at_dt else None
    end_at = end_at_dt.isoformat() if end_at_dt else None

    report_data = ReportService.summary(
        period=period,
        cron_job_id=cron_job_id,
        start_at=start_at,
        end_at=end_at,
    )
    trend_data = ReportService.trend(days=trend_days, cron_job_id=cron_job_id)
    error_data = ReportService.error_summary(
        period=period,
        cron_job_id=cron_job_id,
        start_at=start_at,
        end_at=end_at,
        limit=10,
    )

    return render_template(
        "reports.html",
        report=report_data,
        trend=trend_data,
        errors=error_data,
        jobs=[job.to_dict() for job in CronService.list_all()],
        period=period,
        selected_cron_job_id=cron_job_id,
        selected_start_at=start_at,
        selected_end_at=end_at,
        selected_start_at_local=_to_datetime_local_value(start_at_dt),
        selected_end_at_local=_to_datetime_local_value(end_at_dt),
        trend_days=trend_days,
    )
