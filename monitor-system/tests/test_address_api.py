from __future__ import annotations

from app.routes import address


def test_address_api_accepts_snake_case_payload(client):
    address.service._validate_with_nominatim = lambda payload: (payload, 0.9, "ref-1")

    response = client.post(
        "/api/v1/address/validate",
        json={
            "building_name": "Green Side 5",
            "street_address": "400 Avenue Roumanille",
            "suburb": "Biot",
            "city": "Biot",
            "post_code": "06410",
            "country_code": "FR",
        },
    )

    assert response.status_code == 201
    payload = response.get_json()
    assert payload["validation_status"] == "VALID"
    assert payload["original_address"]["StreetAddress"] == "400 Avenue Roumanille"
    assert payload["original_address"]["CountryCode"] == "FR"


def test_address_api_accepts_nested_address_object(client):
    address.service._validate_with_nominatim = lambda payload: (payload, 0.9, "ref-2")

    response = client.post(
        "/api/v1/address/validate",
        json={
            "address": {
                "StreetAddress": "400 Avenue Roumanille",
                "City": "Biot",
                "CountryCode": "FR",
            }
        },
    )

    assert response.status_code == 201
    payload = response.get_json()
    assert payload["original_address"]["StreetAddress"] == "400 Avenue Roumanille"
    assert payload["original_address"]["City"] == "Biot"
    assert payload["original_address"]["CountryCode"] == "FR"

