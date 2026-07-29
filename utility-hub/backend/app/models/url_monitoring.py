from __future__ import annotations

from datetime import datetime, timezone

from app.utils.extensions import db


class MonitoredURL(db.Model):
    __tablename__ = "monitored_urls"

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False, unique=True, index=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True, index=True)
    notes = db.Column(db.String(255), nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class ExecutionHistory(db.Model):
    __tablename__ = "execution_history"

    id = db.Column(db.Integer, primary_key=True)
    trigger_type = db.Column(db.String(20), nullable=False)
    started_at = db.Column(db.DateTime(timezone=True), nullable=False, index=True)
    ended_at = db.Column(db.DateTime(timezone=True), nullable=False)
    total_duration_ms = db.Column(db.Integer, nullable=False)
    total_urls = db.Column(db.Integer, nullable=False)
    success_count = db.Column(db.Integer, nullable=False)
    failed_count = db.Column(db.Integer, nullable=False)
    overall_status = db.Column(db.String(20), nullable=False)
    initiated_by = db.Column(db.String(120), nullable=True)

    details = db.relationship(
        "ExecutionDetail",
        back_populates="execution_history",
        cascade="all, delete-orphan",
        lazy="select",
    )


class ExecutionDetail(db.Model):
    __tablename__ = "execution_details"

    id = db.Column(db.Integer, primary_key=True)
    execution_history_id = db.Column(
        db.Integer,
        db.ForeignKey("execution_history.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    monitored_url_id = db.Column(
        db.Integer,
        db.ForeignKey("monitored_urls.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    dns_resolved = db.Column(db.Boolean, nullable=False)
    http_status_code = db.Column(db.Integer, nullable=True)
    https_valid = db.Column(db.Boolean, nullable=False)
    response_time_ms = db.Column(db.Integer, nullable=True)
    availability_status = db.Column(db.String(10), nullable=False, index=True)
    error_message = db.Column(db.Text, nullable=True)
    checked_at = db.Column(db.DateTime(timezone=True), nullable=False)

    execution_history = db.relationship("ExecutionHistory", back_populates="details")
    monitored_url = db.relationship("MonitoredURL")
