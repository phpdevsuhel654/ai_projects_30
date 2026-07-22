from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path

from flask import Blueprint, current_app, flash, redirect, render_template, url_for


backup_ui_bp = Blueprint("backup_ui", __name__)


@backup_ui_bp.get("/backup")
def backup_page():
    backup_dir = _get_backup_dir()
    backups = []
    if backup_dir and backup_dir.exists():
        backups = sorted(
            [
                {
                    "name": f.name,
                    "size_kb": round(f.stat().st_size / 1024, 1),
                    "created_at": datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
                }
                for f in backup_dir.glob("*.db")
            ],
            key=lambda x: x["name"],
            reverse=True,
        )
    return render_template("backup.html", backups=backups)


@backup_ui_bp.post("/backup/run")
def run_backup():
    try:
        db_path = _get_db_path()

        if not db_path or not db_path.exists():
            flash(f"Database file not found at {db_path}.", "danger")
            return redirect(url_for("backup_ui.backup_page"))

        backup_dir = _get_backup_dir()
        backup_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"monitor_system_backup_{timestamp}.db"

        shutil.copy2(db_path, backup_path)

        flash(f"Database backed up successfully: {backup_path.name}", "success")
    except Exception as exc:
        flash(f"Backup failed: {exc}", "danger")

    return redirect(url_for("backup_ui.backup_page"))


def _get_db_path() -> Path | None:
    raw = current_app.config.get("DATABASE_PATH")
    if raw:
        return Path(raw)
    uri = current_app.config.get("SQLALCHEMY_DATABASE_URI", "")
    if uri.startswith("sqlite:///"):
        return Path(uri[len("sqlite:///"):])
    return None


def _get_backup_dir() -> Path:
    db_path = _get_db_path()
    if db_path:
        return db_path.parent / "backups"
    return Path(current_app.root_path).parent / "database" / "backups"
