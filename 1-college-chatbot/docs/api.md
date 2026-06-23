# API Documentation

## Base URL
- Local: `http://127.0.0.1:5000`

## Endpoints

### POST /api/chat
Request JSON:
```json
{
  "message": "Tell me about admissions",
  "session_id": "web-session"
}
```

Response JSON:
```json
{
  "response": "...",
  "source": "faq|rag|nlp|llm|fallback|validation",
  "intent": "...",
  "entities": {},
  "confidence": 0.0
}
```

## Notes
- Rate limiting is applied to `/api/chat`.
- LLM fallback requires environment configuration.
