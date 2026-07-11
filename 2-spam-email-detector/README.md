# Spam Email Detector

## Phase 1 Completed

A starter Flask project has been created for the Spam Email Detection System.

### What is included
- Flask application entry point in app.py
- Configuration in config.py
- Home and health routes in routes/home_routes.py
- Base and index templates in templates/
- Dependency list in requirements.txt
- Project folders for database/, routes/, templates/, and static/

### Run the app
```bash
cd d:\AAA_Work\GitHub\ai_projects_30\2-spam-email-detector
C:/Users/L490/AppData/Local/Programs/Python/Python312/python.exe app.py
```

Then open:
- http://127.0.0.1:5000/
- http://127.0.0.1:5000/health

### Verification
The app was verified successfully with:
```bash
C:/Users/L490/AppData/Local/Programs/Python/Python312/python.exe -c "from app import app; print(app.url_map)"
```

### Next step
The next phase will add SQLite configuration and database models.
