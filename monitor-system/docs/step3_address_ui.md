# Step 3 - Address Validation Web UI

## 1) Objective
Add a simple web interface for the Address Validation module while reusing the same service and repository layers.

## 2) Architecture Decisions
- Kept business logic in service layer; UI route only handles form/view concerns.
- Reused existing `AddressValidationService` to avoid duplicated validation logic.
- Rendered history directly from repository-backed data for immediate visibility.

## 3) Folder/File Creation
- app/routes/address_ui.py
- app/templates/base.html
- app/templates/address_validation.html
- docs/step3_address_ui.md

## 4) Implementation Approach
- Added UI blueprint with:
  - `GET /` -> landing page with address form + latest history
  - `GET/POST /address-validation` -> submit address and render result
- Kept REST API endpoints unchanged under `/api/v1/address/...`
- Registered UI blueprint in app factory

## 5) Testing Procedure
1. Start app: `python app.py`
2. Open `http://127.0.0.1:5000/`
3. Submit sample address form
4. Verify:
   - Result panel shows status/confidence/timestamp
   - History table includes the new row
5. Optionally call API:
   - `POST /api/v1/address/validate`
   - `GET /api/v1/address/history?limit=10`
