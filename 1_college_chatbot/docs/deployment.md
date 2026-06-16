# Deployment Guide

## 1) Production Checklist
- Set `APP_ENV=production`
- Set a strong `SECRET_KEY`
- Set `ENABLE_LLM_FALLBACK` based on your budget and API access
- Set `OPENAI_API_KEY` only on server secrets storage
- Set `API_CHAT_RATE_LIMIT` for expected traffic
- Verify `LOG_LEVEL`, `LOG_DIR`, and file permissions

## 2) Gunicorn Run (Linux)
```bash
gunicorn --workers 2 --bind 0.0.0.0:8000 wsgi:app
```

## 3) Docker Build and Run
```bash
docker build -t college-chatbot .
docker run -d --name college-chatbot -p 8000:8000 --env-file .env college-chatbot
```

## 4) Docker Compose
```bash
docker compose up -d --build
```

## 5) Health Verification
- Open `http://localhost:8000/`
- Open `http://localhost:8000/api/docs`
- Check `logs/app.log`

## 6) Notes
- Gunicorn is intended for Linux-based deployment.
- For local Windows production-like runs, use Docker.
