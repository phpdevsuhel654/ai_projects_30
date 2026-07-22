# Step 6 - URL Monitoring Dashboard UI

## 1) Objective
Implement Feature 2 web dashboard to manage monitored URLs and visualize execution outcomes.

## 2) Architecture Decisions
- Reused URLHealthCheckService from UI routes to maintain service/repository separation.
- Kept monitoring REST APIs unchanged and added dedicated UI routes for human workflows.
- Dashboard cards are computed from repository-backed data and latest execution summary.

## 3) Folder/File Creation
- app/routes/monitoring_ui.py
- app/templates/monitoring_dashboard.html
- docs/step6_monitoring_dashboard_ui.md

## 4) Implementation Approach
UI routes:
- GET /url-monitoring
- POST /url-monitoring/add
- POST /url-monitoring/<url_id>/update
- POST /url-monitoring/<url_id>/delete
- POST /url-monitoring/execute

Dashboard includes:
- Total URLs
- Active URLs
- Failed URLs (latest run)
- Last Execution Time
- Execution History
- Latest execution detail table

## 5) Testing Procedure
1. Run app: python app.py
2. Open: http://127.0.0.1:5000/url-monitoring
3. Add URL entries
4. Update and delete URL entries
5. Execute checks via UI button
6. Verify dashboard cards and history table update
