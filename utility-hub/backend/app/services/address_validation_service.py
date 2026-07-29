from __future__ import annotations

import logging

import requests
from flask import current_app

from app.repositories.address_validation_repository import AddressValidationRepository


REQUIRED_ADDRESS_FIELDS = [
    "StreetAddress",
    "City",
    "CountryCode",
]

ADDRESS_FIELD_ALIASES = {
    "BuildingName": ("buildingname", "building_name", "building"),
    "StreetAddress": ("streetaddress", "street_address", "street", "addressline1", "address_line_1"),
    "Suburb": ("suburb", "district", "neighbourhood", "neighborhood"),
    "City": ("city", "town"),
    "PostCode": ("postcode", "post_code", "postalcode", "postal_code", "zip", "zip_code"),
    "CountryCode": ("countrycode", "country_code", "country"),
}

FIELD_ALIAS_TO_CANONICAL = {
    alias: canonical
    for canonical, aliases in ADDRESS_FIELD_ALIASES.items()
    for alias in aliases
}

STREET_ABBREVIATIONS = {
    "ave": "avenue",
    "blvd": "boulevard",
    "cl": "close",
    "ct": "court",
    "dr": "drive",
    "hwy": "highway",
    "ln": "lane",
    "pde": "parade",
    "pl": "place",
    "rd": "road",
    "st": "street",
    "tce": "terrace",
}


logger = logging.getLogger(__name__)


class AddressValidationService:
    def __init__(self, repository: AddressValidationRepository | None = None):
        self.repository = repository or AddressValidationRepository()

    def validate_and_store(self, payload: dict) -> dict:
        payload = self._normalize_payload(payload)
        self._validate_payload(payload)

        corrected_address, confidence, provider_reference = self._validate_with_nominatim(payload)
        validation_status = self._status_from_confidence(confidence)

        record = self.repository.create(
            original_payload=payload,
            corrected_payload=corrected_address,
            validation_status=validation_status,
            confidence_score=confidence,
            provider_name="nominatim",
            provider_reference=provider_reference,
        )
        logger.info(
            "address_validation_completed id=%s status=%s confidence=%.2f",
            record.id,
            validation_status,
            confidence,
        )
        return record.to_dict()

    def history(self, limit: int = 20) -> list[dict]:
        return [row.to_dict() for row in self.repository.get_recent(limit=limit)]

    def _validate_payload(self, payload: dict) -> None:
        if not isinstance(payload, dict):
            raise ValueError("Payload must be a JSON object")

        missing = [field for field in REQUIRED_ADDRESS_FIELDS if not payload.get(field)]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

    def _normalize_payload(self, payload: dict) -> dict:
        if not isinstance(payload, dict):
            return payload

        source_payload = payload
        nested_address = payload.get("address")
        if isinstance(nested_address, dict):
            source_payload = nested_address

        normalized_payload: dict[str, str] = {}
        for raw_key, raw_value in source_payload.items():
            if raw_value is None:
                continue

            key = self._normalize_key(raw_key)
            canonical_key = FIELD_ALIAS_TO_CANONICAL.get(key)
            if not canonical_key:
                continue

            if isinstance(raw_value, str):
                normalized_payload[canonical_key] = raw_value.strip()
            else:
                normalized_payload[canonical_key] = str(raw_value).strip()

        return normalized_payload

    def _normalize_key(self, raw_key: str) -> str:
        return "".join(ch.lower() for ch in str(raw_key) if ch.isalnum())

    def _validate_with_nominatim(self, payload: dict) -> tuple[dict, float, str | None]:
        base_url = current_app.config["NOMINATIM_BASE_URL"].rstrip("/")
        query = ", ".join(
            part for part in [
                payload.get("StreetAddress", ""),
                payload.get("Suburb", ""),
                payload.get("City", ""),
                payload.get("PostCode", ""),
                payload.get("CountryCode", ""),
            ]
            if str(part).strip()
        )

        try:
            response = requests.get(
                f"{base_url}/search",
                headers={
                    "User-Agent": "utility-hub/1.0",
                    "Accept": "application/json",
                },
                params={
                    "q": query,
                    "format": "jsonv2",
                    "addressdetails": 1,
                    "limit": 1,
                    "countrycodes": str(payload.get("CountryCode", "")).lower(),
                },
                timeout=12,
            )
            response.raise_for_status()
            rows = response.json()
        except requests.RequestException:
            return payload, 0.0, None

        if not rows:
            return payload, 0.0, None

        top = rows[0] if isinstance(rows[0], dict) else {}
        addr = top.get("address", {}) if isinstance(top.get("address", {}), dict) else {}

        corrected = {
            "BuildingName": self._first_non_empty_text(payload.get("BuildingName", ""), addr.get("house_name", "")),
            "StreetAddress": self._normalized_street(payload, addr),
            "Suburb": self._first_non_empty_text(payload.get("Suburb", ""), addr.get("suburb", ""), addr.get("neighbourhood", "")),
            "City": self._first_non_empty_text(addr.get("city", ""), addr.get("town", ""), addr.get("village", ""), payload.get("City", "")),
            "PostCode": self._first_non_empty_text(addr.get("postcode", ""), payload.get("PostCode", "")),
            "CountryCode": self._first_non_empty_text(addr.get("country_code", ""), payload.get("CountryCode", "")).upper(),
        }

        confidence = self._calculate_confidence(payload, corrected)
        provider_reference = str(top.get("place_id")) if top.get("place_id") else None
        return corrected, confidence, provider_reference

    def _normalized_street(self, payload: dict, addr: dict) -> str:
        house_number = self._safe_text(addr.get("house_number", ""))
        road = self._safe_text(addr.get("road", ""))

        if house_number and road:
            return f"{house_number} {road}".strip()
        if road:
            return road
        return self._safe_text(payload.get("StreetAddress", ""))

    def _calculate_confidence(self, original: dict, corrected: dict) -> float:
        score = 0.0

        if self._streets_match(original.get("StreetAddress", ""), corrected.get("StreetAddress", "")):
            score += 0.4

        if self._normalized_text(original.get("City", "")) == self._normalized_text(corrected.get("City", "")):
            score += 0.3

        if self._postcodes_match(original.get("PostCode", ""), corrected.get("PostCode", "")):
            score += 0.15

        if self._normalized_token(original.get("CountryCode", "")) == self._normalized_token(
            corrected.get("CountryCode", "")
        ):
            score += 0.15

        score = min(max(score, 0.0), 1.0)
        if score == 0.0:
            score = 0.30

        return round(score, 2)

    def _status_from_confidence(self, confidence: float) -> str:
        if confidence >= 0.8:
            return "VALID"
        if confidence >= 0.45:
            return "PARTIAL"
        if confidence > 0.0:
            return "INVALID"
        return "ERROR"

    def _streets_match(self, left: str, right: str) -> bool:
        left_norm = self._normalized_street_value(left)
        right_norm = self._normalized_street_value(right)
        if left_norm == right_norm:
            return True

        left_stripped = self._strip_leading_number(left_norm)
        right_stripped = self._strip_leading_number(right_norm)
        return bool(left_stripped) and left_stripped == right_stripped

    def _strip_leading_number(self, value: str) -> str:
        parts = value.split()
        if parts and parts[0].isdigit():
            return " ".join(parts[1:])
        return value

    def _normalized_street_value(self, value: str) -> str:
        normalized_tokens: list[str] = []
        for token in self._normalized_text(value).split():
            normalized_tokens.append(STREET_ABBREVIATIONS.get(token, token))
        return " ".join(normalized_tokens)

    def _normalized_token(self, value: str) -> str:
        return "".join(ch.lower() for ch in str(value) if ch.isalnum())

    def _normalized_text(self, value: str) -> str:
        normalized = []
        previous_was_space = False

        for ch in str(value).strip().lower():
            if ch.isalnum():
                normalized.append(ch)
                previous_was_space = False
                continue

            if not previous_was_space:
                normalized.append(" ")
                previous_was_space = True

        return "".join(normalized).strip()

    def _safe_text(self, value: object) -> str:
        if value is None:
            return ""
        return str(value).strip()

    def _first_non_empty_text(self, *values: object) -> str:
        for value in values:
            text = self._safe_text(value)
            if text:
                return text
        return ""

    def _postcodes_match(self, left: str, right: str) -> bool:
        left_token = self._normalized_token(left)
        right_token = self._normalized_token(right)
        if not left_token or not right_token:
            return False

        if left_token == right_token:
            return True

        if any(ch.isalpha() for ch in left_token + right_token):
            return left_token[:3] == right_token[:3]

        return False
