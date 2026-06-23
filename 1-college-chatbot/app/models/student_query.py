from datetime import datetime, timezone

from app.extensions import db


class StudentQuery(db.Model):
    __tablename__ = "student_queries"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    query_text = db.Column(db.Text, nullable=False)
    detected_intent = db.Column(db.String(120), nullable=True)
    entities_json = db.Column(db.Text, nullable=True)
    channel = db.Column(db.String(50), default="web", nullable=False)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    chat_records = db.relationship("ChatHistory", back_populates="query", lazy=True)
