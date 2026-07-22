# Step 2 - Address Validation Module (Initial Slice)

## Objective
Implement the first end-to-end vertical slice for Feature 1:
- POST API to validate an address
- Integrate Nominatim provider
- Persist validation history in SQLite
- GET API to view recent validations

## Folder/File Creation
- app/models/address_validation.py
- app/repositories/address_validation_repository.py
- app/services/address_validation_service.py
- app/routes/address.py
- docs/step2_address_module.md

## Implementation Notes
- Route Layer:
  - `POST /api/v1/address/validate`
  - `GET /api/v1/address/history?limit=20`
- Service Layer:
  - input validation
  - Nominatim request orchestration
  - confidence scoring and status mapping
- Repository Layer:
  - create and fetch recent records
- Model Layer:
  - normalized columns aligned with Step 1 design

## Testing Procedure (Manual)
1. Install dependencies:
   - `pip install -r requirements.txt`
2. Run app:
   - `python app.py`
3. Validate sample payload:
   - `POST /api/v1/address/validate`
4. Fetch history:
   - `GET /api/v1/address/history?limit=10`

Sample request body:
```json
{
  "BuildingName": "Green Side 5",
  "StreetAddress": "400 Avenue Roumanille",
  "Suburb": "Biot",
  "City": "Biot",
  "PostCode": "06410",
  "CountryCode": "FR"
}
```
