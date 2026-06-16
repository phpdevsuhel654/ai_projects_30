from datetime import datetime, timezone

from app.extensions import db


class FAQCategory(db.Model):
    __tablename__ = "faq_categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    knowledge_entries = db.relationship(
        "KnowledgeBase", back_populates="category", lazy=True
    )
