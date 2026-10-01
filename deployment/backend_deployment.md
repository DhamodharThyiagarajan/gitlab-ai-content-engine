# Backend deployment notes

## Recommended stack
- Render or Railway
- Python 3.12 runtime
- Uvicorn service

## Start command
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Required environment variables
- `APP_NAME`
- `APP_ENV`
- `BACKEND_HOST`
- `BACKEND_PORT`
- `FRONTEND_URL`
- `DATABASE_URL`
- `JWT_SECRET`
- `AI_PROVIDER`
- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`
- Firebase credentials
