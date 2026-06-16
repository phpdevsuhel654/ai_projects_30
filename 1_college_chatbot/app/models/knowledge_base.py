from datetime import datetime, timezone

from app.extensions import db


class KnowledgeBase(db.Model):
    __tablename__ = "knowledge_base"

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey("faq_categories.id"), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    source_url = db.Column(db.String(500), nullable=True)
    tags = db.Column(db.String(500), nullable=True)
    is_published = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    category = db.relationship("FAQCategory", back_populates="knowledge_entries")
