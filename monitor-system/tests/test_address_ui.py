from __future__ import annotations

from app.routes import address_ui


def test_address_ui_accepts_json_textarea_and_shows_corrected_json(client):
    address_ui.service.validate_and_store = lambda payload: {
        "id": 1,
        "original_address": payload,
        "corrected_address": {
            "BuildingName": "Green Side 5",
            "StreetAddress": "400 Avenue Roumanille",
            "Suburb": "Sophia Antipolis",
            "City": "Biot",
            "PostCode": "06410",
            "CountryCode": "FR",
        },
        "validation_status": "PARTIAL",
        "confidence_score": 0.7,
        "provider_name": "nominatim",
        "provider_reference": "12345",
        "validation_timestamp": "2026-07-14T00:00:00+00:00",
    }

    response = client.post(
        "/address-validation",
        data={
            "address_json": '{"BuildingName":"Green Side 5","StreetAddress":"400 Avenue Roumanille","Suburb":"Biot","City":"Biot","PostCode":"06410","CountryCode":"FR"}'
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Corrected Address" in response.data
    assert b"Sophia Antipolis" in response.data


def test_address_ui_rejects_invalid_json(client):
    response = client.post(
        "/address-validation",
        data={"address_json": "{invalid-json}"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Invalid JSON format" in response.data
