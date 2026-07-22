from __future__ import annotations

import logging
from datetime import datetime, timezone

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

        logger.info(
            "address_validation_started city=%s country_code=%s",
            payload.get("City"),
            payload.get("CountryCode"),
        )

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

        headers = {
            "User-Agent": "infrastructure-utility-portal/1.0 (learning-project)",
            "Accept": "application/json",
        }

        rows = []
        for query in self._build_query_variants(payload):
            params = {
                "q": query,
                "format": "jsonv2",
                "addressdetails": 1,
                "limit": 1,
                "countrycodes": str(payload.get("CountryCode", "")).lower(),
            }

            try:
                response = requests.get(
                    f"{base_url}/search",
                    headers=headers,
                    params=params,
                    timeout=12,
                )
                response.raise_for_status()
                rows = response.json()
            except requests.RequestException as exc:
                logger.warning("address_provider_call_failed error=%s", exc)
                return payload, 0.0, None

            if rows:
                break

        if not rows:
            logger.info("address_provider_no_match")
            return payload, 0.0, None

        top = rows[0] if isinstance(rows[0], dict) else {}
        raw_address = top.get("address", {})
        addr = raw_address if isinstance(raw_address, dict) else {}

        corrected_suburb, corrected_city = self._resolve_locality(
            payload.get("Suburb", ""),
            payload.get("City", ""),
            addr,
        )
        corrected = {
            "BuildingName": self._first_non_empty_text(payload.get("BuildingName", ""), addr.get("house_name", "")),
            "StreetAddress": self._normalized_street(payload, addr),
            "Suburb": corrected_suburb,
            "City": corrected_city,
            "PostCode": self._first_non_empty_text(addr.get("postcode", ""), payload.get("PostCode", "")),
            "CountryCode": self._first_non_empty_text(addr.get("country_code", ""), payload.get("CountryCode", "")).upper(),
        }

        confidence = self._calculate_confidence(payload, corrected, addr)
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

    def _calculate_confidence(self, original: dict, corrected: dict, provider_address: dict | None = None) -> float:
        score = 0.0
        provider_address = provider_address or {}

        if self._streets_match(original.get("StreetAddress", ""), corrected.get("StreetAddress", "")):
            score += 0.35

        if self._locality_matches(original, provider_address):
            score += 0.25

        if self._postcodes_match(original.get("PostCode", ""), corrected.get("PostCode", "")):
            score += 0.25

        if self._normalized_token(original.get("CountryCode", "")) == self._normalized_token(
            corrected.get("CountryCode", "")
        ):
            score += 0.15

        score = min(max(score, 0.0), 1.0)

        # If no exact field match but we still got a result, treat as low confidence partial.
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

    def _build_query_variants(self, payload: dict) -> list[str]:
        raw_variants = [
            [
                payload.get("BuildingName", ""),
                payload.get("StreetAddress", ""),
                payload.get("Suburb", ""),
                payload.get("City", ""),
                payload.get("PostCode", ""),
                payload.get("CountryCode", ""),
            ],
            [
                payload.get("StreetAddress", ""),
                payload.get("Suburb", ""),
                payload.get("City", ""),
                payload.get("PostCode", ""),
                payload.get("CountryCode", ""),
            ],
            [
                payload.get("StreetAddress", ""),
                payload.get("Suburb", ""),
                payload.get("PostCode", ""),
                payload.get("CountryCode", ""),
            ],
            [
                payload.get("StreetAddress", ""),
                payload.get("City", ""),
                payload.get("PostCode", ""),
                payload.get("CountryCode", ""),
            ],
        ]

        queries: list[str] = []
        seen_queries: set[str] = set()
        for parts in raw_variants:
            query = self._join_unique_parts(parts)
            if not query:
                continue

            normalized_query = self._normalized_text(query)
            if normalized_query in seen_queries:
                continue

            seen_queries.add(normalized_query)
            queries.append(query)

        return queries

    def _join_unique_parts(self, parts: list[str]) -> str:
        unique_parts: list[str] = []
        seen_parts: set[str] = set()

        for part in parts:
            normalized_part = self._normalized_text(part)
            if not normalized_part or normalized_part in seen_parts:
                continue

            seen_parts.add(normalized_part)
            unique_parts.append(str(part).strip())

        return ", ".join(unique_parts)

    def _streets_match(self, left: str, right: str) -> bool:
        left_norm = self._normalized_street_value(left)
        right_norm = self._normalized_street_value(right)
        if left_norm == right_norm:
            return True
        # Nominatim sometimes omits the house number from the road field.
        # Compare again after stripping any leading numeric token from both sides.
        left_stripped = self._strip_leading_number(left_norm)
        right_stripped = self._strip_leading_number(right_norm)
        return bool(left_stripped) and left_stripped == right_stripped

    def _strip_leading_number(self, value: str) -> str:
        """Remove a leading house / building number token from a normalised street string."""
        parts = value.split()
        if parts and parts[0].isdigit():
            return " ".join(parts[1:])
        return value

    def _locality_matches(self, original: dict, provider_address: dict | None = None) -> bool:
        """
        Returns True if either the user's City or Suburb is confirmed by any
        Nominatim locality/state field in the provider response.
        This compares user input directly against the raw provider data so the
        score reflects genuine Nominatim confirmation, not circular self-matching.
        """
        provider_address = provider_address or {}
        original_candidates = {
            self._normalized_text(original.get("City", "")),
            self._normalized_text(original.get("Suburb", "")),
        }
        original_candidates.discard("")
        if not original_candidates:
            return False

        provider_values = {
            self._normalized_text(self._safe_text(provider_address.get(key)))
            for key in (
                "suburb", "neighbourhood", "city_district",
                "city", "town", "village", "municipality",
                "state", "province", "state_district",
            )
        }
        provider_values.discard("")
        return bool(original_candidates.intersection(provider_values))

    def _resolve_locality(self, original_suburb: str, original_city: str, addr: dict) -> tuple[str, str]:
        """
        Determines the corrected Suburb and City from Nominatim's address fields
        without blindly overwriting the user's valid locality values.

        Rules
        -----
        Suburb:
          - If the user's Suburb matches any Nominatim locality field (suburb,
            neighbourhood, city, town, village, state …), use Nominatim's
            capitalisation of that value.
          - Otherwise preserve the user's original Suburb unchanged.
            Nominatim's ``suburb`` / ``neighbourhood`` fields often hold
            sub-district names (e.g. "Sophia Antipolis", "West Springs") that
            are *not* what the user means by Suburb, so we never blindly
            overwrite with them.

        City:
          - If the user's City matches a Nominatim city/town/village/municipality
            field → use Nominatim's capitalisation.
          - If the user's City matches a Nominatim state/province field → keep
            the user's original value.  Users frequently supply province/state as
            the City (e.g. City="Alberta", City="Ontario") and that choice must
            be preserved rather than replaced with the actual city name, which
            would duplicate what is already in Suburb.
          - If neither matches → fall back to the best Nominatim city-level field
            (city → town → village → municipality → user's original).
        """
        nom_suburb_fields = [
            self._safe_text(addr.get("suburb")),
            self._safe_text(addr.get("neighbourhood")),
            self._safe_text(addr.get("city_district")),
        ]
        nom_city_fields = [
            self._safe_text(addr.get("city")),
            self._safe_text(addr.get("town")),
            self._safe_text(addr.get("village")),
            self._safe_text(addr.get("municipality")),
        ]
        nom_state_fields = [
            self._safe_text(addr.get("state")),
            self._safe_text(addr.get("province")),
            self._safe_text(addr.get("state_district")),
        ]

        # Suburb lookup: covers all levels so "PORT LINCOLN" → town "Port Lincoln" is found.
        suburb_lookup = {
            self._normalized_text(v): v
            for v in nom_suburb_fields + nom_city_fields + nom_state_fields
            if v
        }
        # City lookup — city-level fields only.
        city_lookup = {
            self._normalized_text(v): v
            for v in nom_city_fields
            if v
        }
        # State/province lookup — used to detect province-as-city input.
        state_lookup = {
            self._normalized_text(v): v
            for v in nom_state_fields
            if v
        }

        orig_suburb_key = self._normalized_text(original_suburb)
        orig_city_key = self._normalized_text(original_city)

        # Suburb: confirmed by Nominatim → use Nominatim capitalisation; else keep user's value.
        if orig_suburb_key and orig_suburb_key in suburb_lookup:
            corrected_suburb = suburb_lookup[orig_suburb_key]
        else:
            corrected_suburb = original_suburb

        # City resolution (three-way):
        # 1. User's City confirmed as a real city/town  → use Nominatim capitalisation.
        # 2. User's City confirmed as a province/state  → preserve user's original value;
        #    the actual city name already appears (or will appear) in Suburb.
        # 3. Neither matched                            → best available Nominatim city field.
        if orig_city_key and orig_city_key in city_lookup:
            corrected_city = city_lookup[orig_city_key]
        elif orig_city_key and orig_city_key in state_lookup:
            corrected_city = original_city
        else:
            corrected_city = self._first_non_empty_text(*nom_city_fields, original_city)

        return corrected_suburb, corrected_city

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
