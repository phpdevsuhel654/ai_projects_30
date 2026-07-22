# Step 1 - System Architecture

## Objective
Establish a production-ready Flask baseline with clear module boundaries for:
1. Address validation and correction
2. URL health checks and reporting

## Architecture Decisions
- Pattern: Layered architecture using Route -> Service -> Repository -> Model
- Framework: Flask app factory for configuration-based startup
- Persistence: SQLite with SQLAlchemy ORM and Alembic migrations (via Flask-Migrate)
- Config: Environment variables loaded from `.env`
- Background tasks: APScheduler included, enabled later when periodic checks are implemented
- Logging: Python logging module to be configured in Step 2

## Module Boundaries
- `app/routes/`: HTTP endpoints and request/response validation
- `app/services/`: Core business logic
- `app/repositories/`: Data-access abstraction over ORM queries
- `app/models/`: SQLAlchemy entities
- `app/utils/`: Shared helpers (timing, DNS utils, response formatting)
- `app/config/`: Config classes and environment-driven settings

## Runtime Flow
1. Client calls route
2. Route validates input and calls service
3. Service orchestrates external API/network checks and repository operations
4. Repository persists/fetches from SQLite
5. Route returns normalized JSON or renders template

## Initial API Strategy
- REST endpoints under `/api/v1/...`
- UI routes under `/...` for Jinja pages
- Health endpoint `/health` available now for smoke testing

## Selected Free Address API
Primary provider: Nominatim (OpenStreetMap)
- Reason: no mandatory API key for basic usage, stable geocoding coverage, good fit for learning
- Constraint: must respect usage policy and include user-agent in requests (to be added in Step 2)
