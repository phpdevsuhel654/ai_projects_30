# AI-Powered College Enquiry Chatbot System

Learning project path: `ai_projects_30/1_college_chatbot`

## Step 1: Planning and Design (Current Step)

This step covers only:
1. Requirement analysis
2. System architecture
3. Technology stack justification
4. Project folder structure
5. Database schema design

---

## 1) Requirement Analysis

### Core Use Cases
- Student asks college-related questions (admissions, fees, courses, scholarships, placements, hostel, dates, facilities).
- System returns clear conversational responses.
- System stores chat history and query logs.
- Admin manages FAQs and knowledge base.

### Modules
- User module: register, login, profile, history.
- Admin module: FAQ/KB management, users, analytics.
- Chatbot module: intent detection, FAQ match, AI response, context handling.

### Non-Functional
- Secure auth + hashed passwords.
- Input validation and error handling.
- Logging and rate limiting.
- Testable, scalable structure.

---

## 2) System Architecture

Pattern: MVC + Service Layer + Repository Layer

- Routes (Controller): receive requests, validate input, call services.
- Services (Business logic): chatbot pipeline, auth rules, admin rules.
- Repositories (Data access): DB queries through SQLAlchemy models.
- Models (Entity definitions): tables and relations.
- Chatbot Engine: FAQ match -> NLP intent -> RAG -> LLM fallback.

High-level flow:
1. User sends message.
2. Chat service checks session context.
3. FAQ/retrieval search runs first.
4. If confidence low, call LLM.
5. Save query, response, confidence, feedback-ready record.

---

## 3) Technology Stack Justification

- Flask: simple, fast for learning REST + templates.
- SQLite + SQLAlchemy: easy local setup, clean ORM models.
- Flask-Login (or JWT): session auth for web app; JWT optional for API clients.
- Bootstrap 5 + Jinja2: quick responsive UI with server-rendered templates.
- NLP stack:
  - Phase 1: rule/keyword matching.
  - Phase 2: spaCy or NLTK + Sentence Transformers.
  - Phase 3: ChromaDB/FAISS for semantic retrieval (RAG).
  - Phase 4: free/OpenAI-compatible model API integration.

Token/cost control strategy:
- FAQ/retrieval-first pipeline before LLM call.
- Short prompt + short output cap.

---

## 4) Target Folder Structure

```text
college-chatbot/
├── app/
│   ├── routes/
│   ├── services/
│   ├── models/
│   ├── repositories/
│   ├── templates/
│   ├── static/
│   ├── auth/
│   ├── chatbot/
│   ├── utils/
│   └── config/
├── database/
├── tests/
├── docs/
├── requirements.txt
├── run.py
└── README.md
```

Current folder is a starter. We will refactor into this target structure step by step.

---

## 5) Database Schema Design (SQLite)

### Tables
1. users
	- id (PK)
	- full_name
	- email (unique)
	- password_hash
	- role (`student`/`admin`)
	- is_active
	- created_at, updated_at

2. faq_categories
	- id (PK)
	- name (unique)
	- description
	- created_at

3. knowledge_base
	- id (PK)
	- category_id (FK -> faq_categories.id)
	- title
	- content
	- source_url
	- tags
	- is_published
	- created_at, updated_at

4. student_queries
	- id (PK)
	- user_id (FK -> users.id)
	- query_text
	- detected_intent
	- entities_json
	- channel (`web` default)
	- created_at

5. chat_history
	- id (PK)
	- user_id (FK -> users.id)
	- query_id (FK -> student_queries.id)
	- session_id
	- user_message
	- bot_response
	- response_source (`faq`/`retrieval`/`llm`)
	- confidence_score
	- feedback_score (nullable)
	- created_at

6. system_logs
	- id (PK)
	- level (`INFO`/`WARN`/`ERROR`)
	- module
	- message
	- meta_json
	- created_at

---

## Learning Roadmap (Next Steps)

Phase roadmap:
1. Phase 1: Rule-based FAQ chatbot
2. Phase 2: NLP intent + entity extraction
3. Phase 3: RAG + vector search
4. Phase 4: LLM API + context-aware responses

## Next Implementation Step

Step 2 will implement the foundation module only:
- Flask app factory
- Config classes (.env support)
- SQLAlchemy setup
- User model + auth skeleton
- Base templates + Bootstrap layout

We will implement one module at a time with file-by-file explanations and tests.

---

## Step 2: Foundation Module (Implemented)

### Objective
Set up a production-ready base: app factory, environment config, SQLAlchemy, authentication skeleton, template base, and minimal tests.

### Implemented Files
- app/__init__.py
- app/extensions.py
- app/config/settings.py
- app/models/user.py
- app/auth/routes.py
- app/routes/main_routes.py
- app/templates/base.html
- app/templates/index.html
- app/templates/auth/login.html
- app/templates/auth/register.html
- app/templates/auth/profile.html
- app/static/css/style.css
- run.py
- requirements.txt
- .env.example
- tests/conftest.py
- tests/test_app_factory.py
- tests/test_user_model.py

### Run (Local)
1. Create and activate virtual environment
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env`
4. Start app: `python run.py`

### Tests
- Run: `pytest`

### Notes
- Tables auto-create in development by `AUTO_CREATE_TABLES=true`.
- Current auth is a learning skeleton; password reset and stronger validation will be added in later steps.

---

## Step 3: Chatbot Phase 1 (Implemented)

### Objective
Implement a rule-based FAQ chatbot with keyword matching, basic responses, and conversation logging.

### What Was Added
- Chatbot data models: `faq_categories`, `knowledge_base`, `student_queries`, `chat_history`
- Rule-based matching service (`ChatService`) using title/tags token overlap
- Chat repository for saving query + response logs
- Starter FAQ seed data for admissions, fees, hostel, placements
- Chat UI page at `/chat`
- Chat API endpoint at `/api/chat`
- Basic tests for chat page and API behavior

### Endpoints
- `GET /chat` -> chatbot page
- `POST /api/chat` -> accepts `{ message, session_id }`

### Test Status
- `6 passed`

### Next Step
Step 4 will implement NLP intent recognition and entity extraction (Phase 2) with NLTK/spaCy baseline.

---

## Step 4: Chatbot Phase 2 (Implemented)

### Objective
Add NLP-based intent recognition and entity extraction, then integrate it into chat response selection.

### What Was Added
- `NLPEngine` with NLTK tokenization + stemming-based intent scoring
- Entity extraction for year, amount, and program
- Chat flow update: FAQ match -> NLP response -> fallback
- Query logging now stores extracted entities as JSON
- New tests for NLP engine and enhanced API assertions

### Test Status
- `9 passed`

### Next Step
Step 5 will implement RAG basics (vector index + semantic retrieval) for Phase 3.

---

## Step 5: Chatbot Phase 3 (Implemented)

### Objective
Add Retrieval-Augmented Generation (RAG) baseline with vector-style semantic retrieval over the knowledge base.

### What Was Added
- `RAGEngine` with TF-IDF-like vectorization and cosine similarity search
- Chat flow update: FAQ -> RAG retrieval -> NLP -> fallback
- RAG response now references the matched knowledge-base title
- Test fixture now seeds knowledge-base data for deterministic retrieval tests
- New unit tests for RAG engine and chat RAG flow

### Notes
- This is a local lightweight vector retrieval baseline for learning.
- It keeps costs zero and works without external services.
- Next upgrade can switch this engine to ChromaDB or FAISS with sentence embeddings.

### Test Status
- `11 passed`

### Next Step
Step 6 will integrate free/OpenAI-compatible LLM API for Phase 4 context-aware response generation.

---

## Step 6: Chatbot Phase 4 (Implemented)

### Objective
Integrate an OpenAI-compatible LLM fallback with context-aware responses.

### What Was Added
- `LLMClient` for OpenAI-compatible `/chat/completions` API calls
- Config-driven safe enable/disable (`ENABLE_LLM_FALLBACK`)
- Chat flow update: FAQ -> RAG -> NLP -> LLM -> fallback
- Context-aware prompting using recent conversation history
- Token-safe defaults (`OPENAI_MAX_TOKENS=120`)
- Unit test for LLM fallback path (mocked)

### Environment Variables
- `ENABLE_LLM_FALLBACK`
- `OPENAI_BASE_URL`
- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `OPENAI_TIMEOUT_SECONDS`
- `OPENAI_MAX_TOKENS`

### Test Status
- `12 passed`

### Next Step
Step 7 can implement Admin module basics (FAQ/Knowledge CRUD + protected dashboard).

---

## Step 7: Admin Module Basics (Implemented)

### Objective
Add a protected admin area for managing FAQ categories and knowledge base entries.

### What Was Added
- Role-based `admin_required` guard
- Admin dashboard with analytics counts (users, categories, knowledge items, queries, chat records)
- Category CRUD basics (create/list/delete)
- Knowledge base CRUD basics (create/list/delete)
- Admin navigation link visible only to admin users
- Tests for access control and CRUD flow

### Routes
- `GET /admin/` dashboard
- `GET|POST /admin/categories`
- `POST /admin/categories/<id>/delete`
- `GET|POST /admin/knowledge`
- `POST /admin/knowledge/<id>/delete`

### Test Status
- `14 passed`

### Next Step
Step 8 can implement User module completion: password reset flow, profile edit, and chat history screen.

---

## Step 8: User Module Completion (Implemented)

### Objective
Complete core user features: password reset, profile update, and chat history viewing.

### What Was Added
- Profile update form and backend update logic
- Password reset flow with signed time-limited token
- Forgot-password screen that generates demo reset link (learning mode)
- Password reset confirmation screen
- User chat history page (login-protected)
- Navigation links for History and Forgot Password
- Tests for profile update, reset flow, and chat history

### Security Notes
- Reset token is signed using app `SECRET_KEY`
- Token expiry is configurable via `PASSWORD_RESET_MAX_AGE_SECONDS`

### Test Status
- `17 passed`

### Next Step
Step 9 can implement non-functional hardening: rate limiting, structured logging, and API documentation.

---

## Step 9: Non-Functional Hardening (Implemented)

### Objective
Improve security, observability, and developer usability with rate limiting, structured logs, and API docs.

### What Was Added
- Rate limiting via `Flask-Limiter` on `POST /api/chat`
- Configurable rate limit (`API_CHAT_RATE_LIMIT`)
- Structured request logging with request id and rotating log file
- Request tracing header (`X-Request-ID`) on responses
- API docs page (`/api/docs`) and OpenAPI JSON (`/api/openapi.json`)
- Markdown API reference in `docs/api.md`
- Tests for docs endpoint, OpenAPI schema, request id header, and rate limit behavior

### New Config
- `API_CHAT_RATE_LIMIT`
- `RATELIMIT_STORAGE_URI`
- `LOG_LEVEL`
- `LOG_DIR`
- `LOG_FILE_NAME`

### Test Status
- `21 passed`

### Next Step
Step 10 can focus on deployment readiness: production config checklist, Gunicorn setup, and Dockerfile.

---

## Step 10: Deployment Readiness (Implemented)

### Objective
Prepare the project for production-style deployment with Linux WSGI server and containerization.

### What Was Added
- `wsgi.py` entrypoint for Gunicorn
- `Dockerfile` for containerized deployment
- `.dockerignore` for smaller build context
- `docker-compose.yml` for local production-like orchestration
- `docs/deployment.md` with step-by-step deploy checklist and commands
- Production cookie security defaults in config
- `gunicorn` dependency in requirements
- Tests for production config and deployment artifact presence

### Run (Linux server)
- `gunicorn --workers 2 --bind 0.0.0.0:8000 wsgi:app`

### Run (Docker)
- `docker compose up -d --build`

### Test Status
- Added deployment readiness tests (run with full suite)

### Next Step
Step 11 can add CI/CD pipeline basics (lint/test workflow + container build checks).

---

## Step 11: CI/CD Basics (Implemented)

### Objective
Add automated quality checks for tests and deployment artifact validation in a simple CI pipeline.

### What Was Added
- GitHub Actions workflow: `.github/workflows/ci.yml`
- Test matrix for Python 3.11 and 3.12
- Automated test run using `pytest -q`
- Docker image build stage for deployment artifact validation
- CI/CD guide in `docs/ci_cd.md`
- Deployment readiness test updated to verify CI artifacts

### Trigger
- Push to `main`/`master`
- Pull requests to `main`/`master`

### Next Step
Step 12 can add final polish: code cleanup pass, project walkthrough docs, and release checklist.

---

## Step 12: Final Polish and Release Prep (Implemented)

### Objective
Finalize the learning project with operational documentation and release readiness artifacts.

### What Was Added
- `docs/runbook.md` for local/dev/docker operations
- `docs/release_checklist.md` for pre-release and post-release verification
- `docs/project_walkthrough.md` summarizing architecture, runtime flow, and outcomes
- Deployment readiness test extended to validate final documentation artifacts

### Outcome
- The project now has end-to-end implementation, testing, CI checks, deployment files, and release docs.
- Suitable as a complete learning reference from planning to deployment.
