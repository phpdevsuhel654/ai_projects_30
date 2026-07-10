# High-Level Architecture

## Style

- Layered clean architecture with clear separation:
- Controllers: HTTP parsing and response formatting.
- Services: Business workflow and orchestration.
- Repositories: Data access through SQLAlchemy.
- Models: Domain entities and persistence mapping.
- Scheduler: APScheduler orchestration and trigger wiring.
- Reports: Aggregation and summary logic.

## Runtime Flow

1. Client calls REST endpoint.
2. Controller validates request payload.
3. Service executes use case.
4. Repository reads/writes SQLite through SQLAlchemy.
5. Service returns DTO-style dict.
6. Controller serializes to JSON.

## Execution Flow

1. Cron job definition is stored in `cron_jobs`.
2. Manual or scheduled run triggers execution service.
3. Execution service invokes URL using requests with timeout.
4. Each run result is persisted in `execution_logs`.
5. Dashboard and reports aggregate logs by period.
