from datetime import datetime, timezone

from app.utils.extensions import db


class CronJob(db.Model):
    __tablename__ = "cron_jobs"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    execution_count = db.Column(db.Integer, nullable=False, default=1)
    schedule_type = db.Column(db.String(50), nullable=False, default="daily")
    schedule_expression = db.Column(db.String(120), nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    logs = db.relationship(
        "ExecutionLog",
        back_populates="cron_job",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "execution_count": self.execution_count,
            "schedule_type": self.schedule_type,
            "schedule_expression": self.schedule_expression,
            "is_active": self.is_active,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
