# Project Walkthrough

## What You Built
- Flask web app with modular architecture
- Authentication and user profile module
- Admin dashboard and knowledge management
- Multi-phase chatbot pipeline:
  1. FAQ keyword matching
  2. NLP intent/entity extraction
  3. Local RAG retrieval
  4. Optional OpenAI-compatible LLM fallback
- Observability and hardening:
  - Structured logs
  - Request IDs
  - Rate limiting
  - API docs
- Deployment readiness:
  - WSGI entrypoint
  - Docker and compose files
  - CI workflow

## Runtime Flow
1. User sends message to `/api/chat`
2. Pipeline selects answer source in order:
   - FAQ -> RAG -> NLP -> LLM -> fallback
3. Query and response are persisted
4. User can review personal chat history

## Key Learning Outcomes
- Clean app structure (routes/services/repositories/models)
- Incremental feature delivery with tests
- Secure defaults and production awareness
- CI-ready project with reproducible deployment artifacts
