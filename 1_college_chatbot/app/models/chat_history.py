from datetime import datetime, timezone

from app.extensions import db


class ChatHistory(db.Model):
    __tablename__ = "chat_history"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    query_id = db.Column(db.Integer, db.ForeignKey("student_queries.id"), nullable=False)
    session_id = db.Column(db.String(120), nullable=False)
    user_message = db.Column(db.Text, nullable=False)
    bot_response = db.Column(db.Text, nullable=False)
    response_source = db.Column(db.String(50), nullable=False)
    confidence_score = db.Column(db.Float, nullable=True)
    feedback_score = db.Column(db.Integer, nullable=True)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    query = db.relationship("StudentQuery", back_populates="chat_records")
