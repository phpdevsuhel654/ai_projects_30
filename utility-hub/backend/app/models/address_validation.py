from __future__ import annotations

import json
from datetime import datetime, timezone

from app.utils.extensions import db


class AddressValidation(db.Model):
    __tablename__ = "address_validations"

    id = db.Column(db.Integer, primary_key=True)

    building_name = db.Column(db.String(255), nullable=True)
    street_address = db.Column(db.String(255), nullable=False)
    suburb = db.Column(db.String(120), nullable=True)
    city = db.Column(db.String(120), nullable=False)
    post_code = db.Column(db.String(32), nullable=True)
    country_code = db.Column(db.String(8), nullable=False)

    original_payload_json = db.Column(db.Text, nullable=False)
    corrected_payload_json = db.Column(db.Text, nullable=False)

    validation_status = db.Column(db.String(20), nullable=False, index=True)
    confidence_score = db.Column(db.Float, nullable=False)
    provider_name = db.Column(db.String(40), nullable=False)
    provider_reference = db.Column(db.String(120), nullable=True)

    validated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "original_address": self._safe_load_json(self.original_payload_json),
            "corrected_address": self._safe_load_json(self.corrected_payload_json),
            "validation_status": self.validation_status,
            "confidence_score": round(self.confidence_score, 2),
            "provider_name": self.provider_name,
            "provider_reference": self.provider_reference,
            "validation_timestamp": self.validated_at.isoformat(),
        }

    @staticmethod
    def _safe_load_json(raw_json: str) -> dict:
        try:
            value = json.loads(raw_json)
            if isinstance(value, dict):
                return value
        except Exception:
            pass
        return {}
