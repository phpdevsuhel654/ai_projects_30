# User Guide

## 1. Overview
Infrastructure Utility Portal provides two modules:
- Address Validation and Correction
- Server URL Health Monitoring

## 2. Prerequisites
- Python 3.x
- Virtual environment configured
- Dependencies installed from requirements.txt

## 3. Initial Setup
1. Open project root: python/monitor-system
2. Create and activate virtual environment
3. Install dependencies:

```powershell
pip install -r requirements.txt
```

4. Configure environment file:
- Copy .env.example to .env
- Update values if needed

5. Run migrations (if required):

```powershell
flask db upgrade
```

6. Start application:

```powershell
python app.py
```

## 4. Access Points
- Health endpoint: GET /health
- Address UI: GET /address-validation
- URL Monitoring UI: GET /url-monitoring

## 5. Address Validation Module
### 5.1 Validate Address via API
- Endpoint: POST /api/v1/address/validate
- Input: address JSON payload
- Output: original address, corrected address, status, confidence, timestamp
- Required fields: StreetAddress, City, CountryCode
- Accepted key styles: `StreetAddress` / `street_address` / `street`, `CountryCode` / `country_code` / `country`
- You can also send the payload nested as `{ "address": { ... } }`
- For addresses where `Suburb` is the locality and `City` contains a state/region code (for example Australian addresses), include both values; the validator now retries with simplified locality queries automatically.

### 5.2 View Validation History
- Endpoint: GET /api/v1/address/history?limit=20

### 5.3 Use Web UI
- Open /address-validation
- Submit address fields
- Review corrected result and confidence

## 6. URL Monitoring Module
### 6.1 Manage URLs via API
- Add URL: POST /api/v1/monitoring/urls
- List URLs: GET /api/v1/monitoring/urls
- Update URL: PUT /api/v1/monitoring/urls/<url_id>
- Delete URL: DELETE /api/v1/monitoring/urls/<url_id>

### 6.2 Execute Checks
- Manual execution API: POST /api/v1/monitoring/execute
- Dashboard execution: /url-monitoring -> Execute Checks

### 6.3 Reports and History
- Reports list: GET /api/v1/monitoring/reports
- Report detail: GET /api/v1/monitoring/reports/<execution_id>
- History alias: GET /api/v1/monitoring/history

### 6.4 Scheduler (Step 9)
- Status: GET /api/v1/monitoring/scheduler/status
- Run now: POST /api/v1/monitoring/scheduler/run-now
- Config in .env:
  - MONITORING_SCHEDULER_ENABLED
  - MONITORING_SCHEDULER_CRON
  - MONITORING_SCHEDULER_TIMEZONE

## 7. Logging and Troubleshooting
- Application logs: logs/app.log
- Error logs: logs/error.log
- Request tracing includes X-Request-ID

## 8. Testing
Run full test suite:

```powershell
python -m pytest tests -q
```

## 9. Common Issues
- Invalid URL error: ensure URL starts with http:// or https://
- Nominatim throttling: avoid rapid repeated address requests
- Scheduler not running: verify MONITORING_SCHEDULER_ENABLED=true
