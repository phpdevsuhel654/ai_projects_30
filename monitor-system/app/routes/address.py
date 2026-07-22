from __future__ import annotations

from flask import Blueprint, jsonify, request

from app.services.address_validation_service import AddressValidationService


address_bp = Blueprint("address", __name__, url_prefix="/api/v1/address")
service = AddressValidationService()


@address_bp.post("/validate")
def validate_address():
    payload = request.get_json(silent=True) or {}

    try:
        result = service.validate_and_store(payload)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(result), 201


@address_bp.get("/history")
def address_history():
    limit_arg = request.args.get("limit", "20")

    try:
        limit = int(limit_arg)
    except ValueError:
        return jsonify({"error": "limit must be an integer"}), 400

    return jsonify({"items": service.history(limit=limit)}), 200
