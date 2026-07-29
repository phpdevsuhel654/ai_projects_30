from __future__ import annotations

import json

from app.models.address_validation import AddressValidation
from app.utils.extensions import db


class AddressValidationRepository:
    def create(
        self,
        original_payload: dict,
        corrected_payload: dict,
        validation_status: str,
        confidence_score: float,
        provider_name: str,
        provider_reference: str | None,
    ) -> AddressValidation:
        record = AddressValidation(
            building_name=original_payload.get("BuildingName"),
            street_address=original_payload.get("StreetAddress", ""),
            suburb=original_payload.get("Suburb"),
            city=original_payload.get("City", ""),
            post_code=original_payload.get("PostCode"),
            country_code=original_payload.get("CountryCode", ""),
            original_payload_json=json.dumps(original_payload, ensure_ascii=True),
            corrected_payload_json=json.dumps(corrected_payload, ensure_ascii=True),
            validation_status=validation_status,
            confidence_score=confidence_score,
            provider_name=provider_name,
            provider_reference=provider_reference,
        )
        db.session.add(record)
        db.session.commit()
        return record

    def get_recent(self, limit: int = 20) -> list[AddressValidation]:
        safe_limit = max(1, min(limit, 100))
        return (
            AddressValidation.query.order_by(AddressValidation.validated_at.desc())
            .limit(safe_limit)
            .all()
        )
