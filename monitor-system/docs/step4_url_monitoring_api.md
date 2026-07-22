# Step 4 - URL Monitoring REST API Module

## 1) Objective
Implement the first backend slice of Feature 2 with:
- URL CRUD
- One-click execution of health checks
- Report/history APIs

## 2) Architecture Decisions
- Route layer only handles HTTP concerns.
- Service layer performs DNS, HTTP, HTTPS, response timing, and status evaluation.
- Repository layer persists URL master data and execution records.
- Model layer stores normalized execution header/detail records.

## 3) Folder/File Creation
- app/models/url_monitoring.py
- app/repositories/url_monitoring_repository.py
- app/services/url_health_check_service.py
- app/routes/monitoring.py
- docs/step4_url_monitoring_api.md

## 4) API Endpoints
- POST /api/v1/monitoring/urls
- GET /api/v1/monitoring/urls
- PUT /api/v1/monitoring/urls/<url_id>
- DELETE /api/v1/monitoring/urls/<url_id>
- POST /api/v1/monitoring/execute
- GET /api/v1/monitoring/reports
- GET /api/v1/monitoring/reports/<execution_id>
- GET /api/v1/monitoring/history

## 5) Testing Procedure
1. Start app: python app.py
2. Add URL:
   POST /api/v1/monitoring/urls
   body: {"url":"https://web4.omniparcelreturns.com","is_active":true}
3. Execute check:
   POST /api/v1/monitoring/execute
4. View summary:
   GET /api/v1/monitoring/reports?limit=10
5. View detail:
   GET /api/v1/monitoring/reports/<execution_id>
