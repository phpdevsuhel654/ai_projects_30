# Release Checklist

## Pre-Release
- [ ] All tests pass locally (`pytest -q`)
- [ ] CI workflow green
- [ ] `.env` values reviewed for target environment
- [ ] `SECRET_KEY` set securely in deployment secrets
- [ ] LLM configuration validated (if enabled)
- [ ] API rate limits reviewed
- [ ] Logs path writable by runtime user

## Deployment
- [ ] Container image builds successfully
- [ ] Service reachable on target host/port
- [ ] `/api/docs` and `/api/openapi.json` reachable
- [ ] Admin login works with admin role
- [ ] Chat endpoint responds within expected latency

## Post-Release
- [ ] Check `logs/app.log` for startup/runtime errors
- [ ] Verify request tracing with `X-Request-ID`
- [ ] Smoke-test user flows (register/login/chat/history)
- [ ] Smoke-test admin flows (categories/knowledge CRUD)
