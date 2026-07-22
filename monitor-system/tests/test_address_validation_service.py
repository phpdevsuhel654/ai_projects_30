from __future__ import annotations

from app.services.address_validation_service import AddressValidationService


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


def test_address_service_handles_suburb_and_state_style_australian_address(app, monkeypatch):
    service = AddressValidationService()
    queries = []

    def fake_get(url, headers, params, timeout):
        queries.append(params["q"])
        # Real Nominatim shape: neighbourhood is a sub-district, town is the actual locality.
        return FakeResponse(
            [
                {
                    "place_id": 12345,
                    "address": {
                        "road": "Verran Terrace",
                        "neighbourhood": "Lincoln Gardens",
                        "town": "Port Lincoln",
                        "state": "South Australia",
                        "postcode": "5606",
                        "country_code": "au",
                    },
                }
            ]
        )

    monkeypatch.setattr("app.services.address_validation_service.requests.get", fake_get)

    with app.app_context():
        result = service.validate_and_store(
            {
                "BuildingName": "91 Verran Tce",
                "StreetAddress": "91 Verran Tce",
                "Suburb": "PORT LINCOLN",
                "City": "SA",
                "PostCode": "5606",
                "CountryCode": "AU",
            }
        )

    assert queries == ["91 Verran Tce, PORT LINCOLN, SA, 5606, AU"]
    assert result["validation_status"] == "VALID"
    assert result["confidence_score"] == 1.0
    assert result["corrected_address"]["StreetAddress"] == "Verran Terrace"
    # "PORT LINCOLN" confirmed via town field → corrected with Nominatim capitalisation
    assert result["corrected_address"]["Suburb"] == "Port Lincoln"
    # SA not found in city fields → resolved to best Nominatim city field (town)
    assert result["corrected_address"]["City"] == "Port Lincoln"
    # neighbourhood sub-district must NOT overwrite user's suburb
    assert result["corrected_address"]["Suburb"] != "Lincoln Gardens"


def test_address_service_retries_with_simpler_query_when_first_search_has_no_match(app, monkeypatch):
    service = AddressValidationService()
    queries = []

    def fake_get(url, headers, params, timeout):
        queries.append(params["q"])
        if len(queries) == 1:
            return FakeResponse([])

        return FakeResponse(
            [
                {
                    "place_id": 67890,
                    "address": {
                        "road": "Verran Terrace",
                        "neighbourhood": "Lincoln Gardens",
                        "town": "Port Lincoln",
                        "state": "South Australia",
                        "postcode": "5606",
                        "country_code": "au",
                    },
                }
            ]
        )

    monkeypatch.setattr("app.services.address_validation_service.requests.get", fake_get)

    with app.app_context():
        result = service.validate_and_store(
            {
                "BuildingName": "91 Verran Tce",
                "StreetAddress": "91 Verran Tce",
                "Suburb": "PORT LINCOLN",
                "City": "SA",
                "PostCode": "5606",
                "CountryCode": "AU",
            }
        )

    assert queries == [
        "91 Verran Tce, PORT LINCOLN, SA, 5606, AU",
        "91 Verran Tce, PORT LINCOLN, 5606, AU",
    ]
    assert result["validation_status"] == "VALID"
    assert result["provider_reference"] == "67890"
    # neighbourhood sub-district must NOT overwrite the suburb
    assert result["corrected_address"]["Suburb"] != "Lincoln Gardens"


def test_address_service_handles_canadian_province_and_postal_prefix_match(app, monkeypatch):
    service = AddressValidationService()

    def fake_get(url, headers, params, timeout):
        return FakeResponse(
            [
                {
                    "place_id": 47015769,
                    "address": {
                        "house_number": "291",
                        "road": "Ramsay Street",
                        "town": "Amherstburg",
                        "state": "Ontario",
                        "postcode": "N9V 1H8",
                        "country_code": "ca",
                    },
                }
            ]
        )

    monkeypatch.setattr("app.services.address_validation_service.requests.get", fake_get)

    with app.app_context():
        result = service.validate_and_store(
            {
                "BuildingName": "291 Ramsay street",
                "StreetAddress": "291 Ramsay street",
                "Suburb": "Amherstburg",
                "City": "Ontario",
                "PostCode": "N9v1y3",
                "CountryCode": "CA",
            }
        )

    assert result["validation_status"] == "VALID"
    assert result["confidence_score"] == 1.0
    assert result["corrected_address"]["StreetAddress"] == "291 Ramsay Street"
    # "Ontario" is a province confirmed in state field → must be preserved, not replaced with "Amherstburg"
    assert result["corrected_address"]["City"] == "Ontario"
    # Suburb "Amherstburg" confirmed via town field → preserved with Nominatim capitalisation
    assert result["corrected_address"]["Suburb"] == "Amherstburg"


def test_address_service_tolerates_null_provider_fields(app, monkeypatch):
    service = AddressValidationService()

    def fake_get(url, headers, params, timeout):
        return FakeResponse(
            [
                {
                    "place_id": 55555,
                    "address": {
                        "house_number": None,
                        "road": None,
                        "town": "Amherstburg",
                        "postcode": "N9V 1Y3",
                        "country_code": "ca",
                    },
                }
            ]
        )

    monkeypatch.setattr("app.services.address_validation_service.requests.get", fake_get)

    with app.app_context():
        result = service.validate_and_store(
            {
                "StreetAddress": "291 Ramsay street",
                "Suburb": "Amherstburg",
                "City": "Ontario",
                "PostCode": "N9V1Y3",
                "CountryCode": "CA",
            }
        )

    assert result["validation_status"] in {"PARTIAL", "VALID"}
    assert result["corrected_address"]["StreetAddress"] == "291 Ramsay street"


def test_address_service_does_not_overwrite_suburb_with_nominatim_sub_district(app, monkeypatch):
    """
    Nominatim's 'suburb' field often contains a business-park or administrative
    sub-district name (e.g. "Sophia Antipolis" for addresses in Biot, France).
    The corrected Suburb must reflect the user's input locality, not the
    Nominatim sub-district, when the user's value is confirmed via another field.
    """
    service = AddressValidationService()

    def fake_get(url, headers, params, timeout):
        return FakeResponse(
            [
                {
                    "place_id": 99001,
                    "address": {
                        "house_number": "400",
                        "road": "Avenue Roumanille",
                        "suburb": "Sophia Antipolis",   # sub-district, NOT the locality
                        "village": "Biot",              # this is the actual locality
                        "postcode": "06410",
                        "country_code": "fr",
                    },
                }
            ]
        )

    monkeypatch.setattr("app.services.address_validation_service.requests.get", fake_get)

    with app.app_context():
        result = service.validate_and_store(
            {
                "BuildingName": "Green Side 5",
                "StreetAddress": "400 Avenue Roumanille",
                "Suburb": "Biot",
                "City": "Biot",
                "PostCode": "06410",
                "CountryCode": "FR",
            }
        )

    corrected = result["corrected_address"]
    # Suburb must be "Biot" (confirmed via village), never "Sophia Antipolis"
    assert corrected["Suburb"] == "Biot"
    assert corrected["Suburb"] != "Sophia Antipolis"
    assert corrected["City"] == "Biot"
    assert result["validation_status"] == "VALID"


def test_address_service_preserves_province_as_city_for_calgary(app, monkeypatch):
    """
    User supplies Suburb="Calgary" (the actual city) and City="Alberta" (the province).
    Nominatim returns city="Calgary" and state="Alberta".
    - Suburb must remain "Calgary" (confirmed via Nominatim's city field).
    - City must remain "Alberta" (confirmed as province in state field) and must NOT
      be overwritten with "Calgary", which would duplicate the Suburb.
    """
    service = AddressValidationService()

    def fake_get(url, headers, params, timeout):
        return FakeResponse(
            [
                {
                    "place_id": 77001,
                    "address": {
                        "house_number": "60",
                        "road": "Wentwillow Lane SW",
                        "suburb": "West Springs",
                        "city": "Calgary",
                        "state": "Alberta",
                        "postcode": "T3H 5K2",
                        "country_code": "ca",
                    },
                }
            ]
        )

    monkeypatch.setattr("app.services.address_validation_service.requests.get", fake_get)

    with app.app_context():
        result = service.validate_and_store(
            {
                "BuildingName": "60 Wentwillow lane sw",
                "StreetAddress": "60 Wentwillow lane sw",
                "Suburb": "Calgary",
                "City": "Alberta",
                "PostCode": "T3h5w7",
                "CountryCode": "CA",
            }
        )

    corrected = result["corrected_address"]
    # Suburb confirmed via Nominatim city field → use Nominatim capitalisation
    assert corrected["Suburb"] == "Calgary"
    # Province must not overwrite suburb; "West Springs" sub-district must not overwrite either
    assert corrected["Suburb"] != "West Springs"
    # City confirmed as province → preserved, not replaced with the city name
    assert corrected["City"] == "Alberta"
    assert corrected["City"] != "Calgary"
    # PostCode corrected by Nominatim
    assert corrected["PostCode"] == "T3H 5K2"
    assert result["validation_status"] == "VALID"
