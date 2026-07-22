from __future__ import annotations

import json

from flask import Blueprint, render_template, request

from app.services.address_validation_service import AddressValidationService


address_ui_bp = Blueprint("address_ui", __name__)
service = AddressValidationService()


@address_ui_bp.route("/", methods=["GET"])
def home():
    return render_template(
        "address_validation.html",
        history=service.history(limit=20),
        address_json_input="",
        error=None,
        result=None,
        corrected_json_output="",
    )


@address_ui_bp.route("/address-validation", methods=["GET", "POST"])
def address_validation_page():
    address_json_input = ""
    result = None
    error = None
    corrected_json_output = ""

    if request.method == "POST":
        address_json_input = request.form.get("address_json", "").strip()

        try:
            payload = json.loads(address_json_input)
            result = service.validate_and_store(payload)
            corrected_json_output = json.dumps(result.get("corrected_address", {}), indent=2, ensure_ascii=True)
        except json.JSONDecodeError:
            error = "Invalid JSON format. Please provide a valid JSON object."
        except ValueError as exc:
            error = str(exc)

    history = service.history(limit=20)
    return render_template(
        "address_validation.html",
        history=history,
        address_json_input=address_json_input,
        error=error,
        result=result,
        corrected_json_output=corrected_json_output,
    )
