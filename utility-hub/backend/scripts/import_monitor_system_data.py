from __future__ import annotations

import argparse
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import create_app
from app.models.address_validation import AddressValidation
from app.models.url_monitoring import ExecutionDetail, ExecutionHistory, MonitoredURL
from app.utils.extensions import db


def _parse_datetime(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    text = str(value).strip()
    if not text:
        return None
    # SQLite rows may store UTC values with trailing Z.
    return datetime.fromisoformat(text.replace("Z", "+00:00"))


def _table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,),
    ).fetchone()
    return row is not None


def _fetch_rows(conn: sqlite3.Connection, table_name: str) -> list[sqlite3.Row]:
    if not _table_exists(conn, table_name):
        return []
    return conn.execute(f"SELECT * FROM {table_name}").fetchall()


def import_data(source_db_path: Path) -> dict:
    if not source_db_path.exists():
        raise FileNotFoundError(f"Source database not found: {source_db_path}")

    conn = sqlite3.connect(source_db_path)
    conn.row_factory = sqlite3.Row

    url_id_map: dict[int, int] = {}
    imported = {
        "address_validations": 0,
        "monitored_urls": 0,
        "execution_history": 0,
        "execution_details": 0,
    }

    source_addresses = _fetch_rows(conn, "address_validations")
    source_urls = _fetch_rows(conn, "monitored_urls")
    source_history = _fetch_rows(conn, "execution_history")
    source_details = _fetch_rows(conn, "execution_details")

    # De-dupe by stable tuple to avoid duplicate imports across repeated runs.
    existing_address_keys = {
        (
            row.provider_reference,
            row.validation_status,
            row.street_address,
            row.city,
            row.validated_at.isoformat() if row.validated_at else "",
        )
        for row in AddressValidation.query.all()
    }

    for row in source_addresses:
        key = (
            row["provider_reference"],
            row["validation_status"],
            row["street_address"],
            row["city"],
            str(row["validated_at"] or ""),
        )
        if key in existing_address_keys:
            continue

        db.session.add(
            AddressValidation(
                building_name=row["building_name"],
                street_address=row["street_address"],
                suburb=row["suburb"],
                city=row["city"],
                post_code=row["post_code"],
                country_code=row["country_code"],
                original_payload_json=row["original_payload_json"],
                corrected_payload_json=row["corrected_payload_json"],
                validation_status=row["validation_status"],
                confidence_score=row["confidence_score"],
                provider_name=row["provider_name"],
                provider_reference=row["provider_reference"],
                validated_at=_parse_datetime(row["validated_at"]),
                created_at=_parse_datetime(row["created_at"]),
            )
        )
        existing_address_keys.add(key)
        imported["address_validations"] += 1

    existing_urls = {row.url: row for row in MonitoredURL.query.all()}
    for row in source_urls:
        existing = existing_urls.get(row["url"])
        if existing:
            url_id_map[int(row["id"])] = int(existing.id)
            continue

        target = MonitoredURL(
            url=row["url"],
            is_active=bool(row["is_active"]),
            notes=row["notes"],
            created_at=_parse_datetime(row["created_at"]),
            updated_at=_parse_datetime(row["updated_at"]),
        )
        db.session.add(target)
        db.session.flush()

        existing_urls[target.url] = target
        url_id_map[int(row["id"])] = int(target.id)
        imported["monitored_urls"] += 1

    existing_history_keys = {
        (
            row.trigger_type,
            row.started_at.isoformat() if row.started_at else "",
            row.ended_at.isoformat() if row.ended_at else "",
            row.total_urls,
            row.success_count,
            row.failed_count,
        ): row.id
        for row in ExecutionHistory.query.all()
    }

    history_id_map: dict[int, int] = {}
    for row in source_history:
        key = (
            row["trigger_type"],
            str(row["started_at"] or ""),
            str(row["ended_at"] or ""),
            row["total_urls"],
            row["success_count"],
            row["failed_count"],
        )

        if key in existing_history_keys:
            history_id_map[int(row["id"])] = int(existing_history_keys[key])
            continue

        target = ExecutionHistory(
            trigger_type=row["trigger_type"],
            started_at=_parse_datetime(row["started_at"]),
            ended_at=_parse_datetime(row["ended_at"]),
            total_duration_ms=row["total_duration_ms"],
            total_urls=row["total_urls"],
            success_count=row["success_count"],
            failed_count=row["failed_count"],
            overall_status=row["overall_status"],
            initiated_by=row["initiated_by"],
        )
        db.session.add(target)
        db.session.flush()

        existing_history_keys[key] = target.id
        history_id_map[int(row["id"])] = int(target.id)
        imported["execution_history"] += 1

    existing_detail_keys = {
        (
            row.execution_history_id,
            row.monitored_url_id,
            row.availability_status,
            row.http_status_code,
            row.checked_at.isoformat() if row.checked_at else "",
        )
        for row in ExecutionDetail.query.all()
    }

    for row in source_details:
        source_history_id = int(row["execution_history_id"])
        source_url_id = int(row["monitored_url_id"])

        target_history_id = history_id_map.get(source_history_id)
        target_url_id = url_id_map.get(source_url_id)
        if target_history_id is None or target_url_id is None:
            continue

        key = (
            target_history_id,
            target_url_id,
            row["availability_status"],
            row["http_status_code"],
            str(row["checked_at"] or ""),
        )
        if key in existing_detail_keys:
            continue

        db.session.add(
            ExecutionDetail(
                execution_history_id=target_history_id,
                monitored_url_id=target_url_id,
                dns_resolved=bool(row["dns_resolved"]),
                http_status_code=row["http_status_code"],
                https_valid=bool(row["https_valid"]),
                response_time_ms=row["response_time_ms"],
                availability_status=row["availability_status"],
                error_message=row["error_message"],
                checked_at=_parse_datetime(row["checked_at"]),
            )
        )
        existing_detail_keys.add(key)
        imported["execution_details"] += 1

    db.session.commit()
    conn.close()
    return imported


def main() -> int:
    parser = argparse.ArgumentParser(description="Import monitor-system records into Utility Hub")
    default_source = (
        Path(__file__).resolve().parents[3]
        / "monitor-system"
        / "database"
        / "monitor_system.db"
    )
    parser.add_argument(
        "--source-db",
        default=str(default_source),
        help="Path to monitor-system SQLite database",
    )
    args = parser.parse_args()

    app = create_app({"SCHEDULER_ENABLED": False, "MONITORING_SCHEDULER_ENABLED": False})
    source_db_path = Path(args.source_db).expanduser().resolve()

    with app.app_context():
        result = import_data(source_db_path)

    print("Import completed:")
    for key, value in result.items():
        print(f"- {key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
