# Step 5 - Database Migrations and Initialization

## 1) Objective
Create a reliable database migration workflow so schema changes are versioned and reproducible across environments.

## 2) Architecture Decisions
- Use Flask-Migrate (Alembic) for migration generation and upgrade operations.
- Keep all model metadata imported through app factory so autogenerate can detect all tables.
- Keep SQLite file under database/ as configured by DATABASE_PATH.

## 3) Folder/File Creation
- docs/step5_migrations_and_db_init.md
- migrations/alembic.ini
- migrations/env.py
- migrations/script.py.mako
- migrations/versions/447243cda2a3_initial_schema.py
- database/monitor_system.db

## 4) Implementation Approach
1. Ensure env variables are loaded from .env via python-dotenv.
2. Set Flask CLI runtime variables in .env:
   - FLASK_APP=app.py
   - FLASK_ENV=development
3. Initialize migrations folder once.
4. Generate first migration from current models.
5. Apply migration to create database schema.

## 5) Commands (Windows PowerShell)
Run these from project root:

```powershell
python -m pip install -r requirements.txt
flask db init
flask db migrate -m "initial schema"
flask db upgrade
```

If migrations are already initialized:

```powershell
flask db migrate -m "schema update"
flask db upgrade
```

## 6) Validation Procedure
1. Verify migration files exist under migrations/versions.
2. Verify database file exists at database/monitor_system.db.
3. Run app:
   - python app.py
4. Smoke-check endpoints:
   - GET /health
   - GET /api/v1/address/history
   - GET /api/v1/monitoring/urls

## 7) This Step Execution Status
- Dependencies installed in project virtual environment.
- Migration init completed.
- Initial migration generated.
- Database upgraded successfully.
