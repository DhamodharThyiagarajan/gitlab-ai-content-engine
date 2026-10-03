# Backend Deployment on Render

This project’s backend is a FastAPI app located in the `backend` folder. It is configured in [backend/app/main.py](../backend/app/main.py) and [backend/app/config.py](../backend/app/config.py).

## 1) Create the Render service

1. Open https://dashboard.render.com
2. Click New + → Web Service
3. Connect your GitHub repository
4. Choose the repo and set:
   - Name: `gitlab-ai-content-engine-api`
   - Root Directory: `backend`
   - Runtime: `Python`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## 2) Required environment variables

Set these in Render → Environment:

```env
APP_NAME=GitLab AI Content Engine
APP_ENV=production
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
FRONTEND_URL=https://your-vercel-app.vercel.app
DATABASE_URL=postgresql+psycopg://user:password@host:5432/dbname
AUTH_PROVIDER=firebase
FIREBASE_PROJECT_ID=your-firebase-project-id
JWT_SECRET=chae-this-to-a-long-random-secretng
JWT_EXPIRE_MINUTES=1440
AI_PROVIDER=mock
CORS_ORIGINS=https://your-vercel-app.vercel.app
```

### Optional AI keys

```env
AI_PROVIDER=openai_compatible
OPENAI_API_KEY=your_key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4.1-mini
AI_TIMEOUT_SECONDS=120
```

### Firebase admin configuration

Choose one of these methods:

```env
FIREBASE_SERVICE_ACCOUNT_JSON={"type":"service_account",...}
```

or

```env
FIREBASE_SERVICE_ACCOUNT_PATH=/app/serviceAccountKey.json
```

> For production, the safer choice is usually a JSON secret or a mounted secret file.

## 3) Database recommendation

Do not use SQLite in production. The app supports PostgreSQL.

Example:

```env
DATABASE_URL=postgresql+psycopg://postgres:yourpassword@db.xxxxxx.supabase.co:5432/postgres
```

Render Postgres or Supabase Postgres is recommended.

## 4) CORS setup

The backend reads `CORS_ORIGINS` in [backend/app/config.py](../backend/app/config.py) and applies it in [backend/app/main.py](../backend/app/main.py).

If your frontend is deployed on Vercel, include the frontend URL:

```env
CORS_ORIGINS=https://your-vercel-app.vercel.app
```

## 5) Health checks

After deployment, confirm the backend is alive:

```bash
https://your-render-service.onrender.com/health
```

Expected response:

```json
{"status":"ok","service":"GitLab AI Content Engine"}
```

You can also check:

```bash
https://your-render-service.onrender.com/health/ready
```

## 6) Deployment tips

- Keep the backend on Render and the frontend on Vercel.
- Use Postgres instead of SQLite.
- Set `CORS_ORIGINS` exactly to your Vercel domain.
- Keep all secrets in Render environment variables.
- Redeploy after every env var change.

## 7) Example final backend URL

```text
https://gitlab-ai-content-engine-api.onrender.com
```

Use this value in Vercel as:

```env
NEXT_PUBLIC_BACKEND_URL=https://gitlab-ai-content-engine-api.onrender.com
```
