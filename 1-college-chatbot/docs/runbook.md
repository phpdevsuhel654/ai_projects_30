# Runbook

## Local Development
1. Create virtual environment
2. Install dependencies
   - `pip install -r requirements.txt`
3. Copy env file
   - `.env.example` -> `.env`
4. Start app
   - `python run.py`
5. Open app
   - `http://127.0.0.1:5000/`

## Test Execution
- Run all tests:
  - `pytest -q`

## Docker Run
1. Build image
   - `docker build -t college-chatbot .`
2. Run container
   - `docker run -d --name college-chatbot -p 8000:8000 --env-file .env college-chatbot`
3. Verify
   - `http://localhost:8000/`

## Common Operational Checks
- API docs endpoint: `/api/docs`
- OpenAPI JSON: `/api/openapi.json`
- Log file: `logs/app.log`
- Request trace header: `X-Request-ID`
