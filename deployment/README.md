# Deployment plan

This repository has a working local stack and verified backend/frontend build status. The remaining deployment work is external hosting configuration, which requires live provider credentials.

## Recommended production deployment

### Frontend
- Provider: Vercel
- Project root: repository root, so Vercel reads the root `vercel.json`
- Install command: `cd frontend && npm ci`
- Build command: `cd frontend && npm run build`
- Output directory: `frontend/.next`
- Environment variables:
  - `NEXT_PUBLIC_BACKEND_URL` set to the deployed backend origin
  - Firebase public config values from `frontend/.env.example`

### Backend
- Provider: Render or Railway
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Environment variables:
  - `APP_NAME=GitLab AI Content Engine`
  - `APP_ENV=production`
  - `BACKEND_HOST=0.0.0.0`
  - `BACKEND_PORT=8000`
  - `FRONTEND_URL=https://your-frontend-url`
  - `DATABASE_URL=postgresql+psycopg://...`
  - `AUTH_PROVIDER=firebase`
  - `FIREBASE_PROJECT_ID=...`
  - `FIREBASE_PROJECT_ID=...`
  - `FIREBASE_SERVICE_ACCOUNT_JSON=...` or application-default credentials
  - `JWT_SECRET=...`
  - `CORS_ORIGINS=https://your-frontend-domain.example`
  - `AI_PROVIDER=mock` or `openai_compatible`
  - `OPENAI_API_KEY=...`
  - `OPENAI_BASE_URL=https://api.openai.com/v1`

### Database
- Supabase PostgreSQL is the intended production database for application data.
- For local trials, SQLite can be used when the app is configured accordingly.

### Firebase
- Configure Firebase Authentication in the project.
- Add the public config to the frontend and the service account JSON or ADC to the backend.

## Local verification already completed

- `python -m pytest -q` passes in the repo venv
- `npm run build` passes in `frontend`
- `curl http://localhost:8000/health` returns the backend status payload

## Final public deployment requirement

To satisfy the full pasted brief, the application still needs:

1. A live frontend deployment URL
2. A live backend deployment URL
3. A production database connection
4. Firebase + Supabase credentials configured in the live environment
5. A public demo video and app link for the final submission package

These cannot be generated from this local workspace alone without actual hosted infrastructure access.

## Live deployment checklist

### 1) Frontend on Vercel

1. Import the repository into Vercel.
2. Set the project root to the repository root so it reads `vercel.json`.
3. Use these build settings:
  - Framework: Next.js
  - Install command: `cd frontend && npm ci`
  - Build command: `cd frontend && npm run build`
  - Output directory: `frontend/.next`
4. Add environment variables:
  - `NEXT_PUBLIC_BACKEND_URL=https://your-render-backend-url`
  - Firebase public values from your Firebase project

### 2) Backend on Render or Railway

1. Deploy the backend service from the repo root or from the `backend` folder, depending on provider.
2. The manifest uses the provider-assigned `$PORT` in its runtime command.
3. Add environment variables from `backend/.env.example`:
  - `APP_NAME`
  - `APP_ENV=production`
  - `FRONTEND_URL=https://your-frontend-domain.example`
  - `DATABASE_URL=postgresql+psycopg://...`
  - `AUTH_PROVIDER=firebase`
  - `FIREBASE_PROJECT_ID=...`
  - `FIREBASE_SERVICE_ACCOUNT_JSON=...` or application-default credentials
  - `JWT_SECRET=...`
  - `AI_PROVIDER=openai_compatible`
  - `OPENAI_API_KEY=...`
  - `OPENAI_BASE_URL=https://api.openai.com/v1`
  - `CORS_ORIGINS=https://your-frontend-domain.example`
4. Confirm the health endpoint responds on `/health`.

### 3) Production data and auth

- Use Supabase PostgreSQL for the production application database.
- Use Firebase Authentication for login and token validation.
- Ensure the backend service account JSON or ADC credentials are available in the live environment.

### 4) Final public launch

Once the Vercel and Render/Railway projects are connected and the environment variables are set:

- Vercel provides the public frontend URL
- Render/Railway provides the public backend URL
- Update `NEXT_PUBLIC_BACKEND_URL` in Vercel to the final backend URL
- Test the full app flow:
  - signup/login
  - create content job
  - review draft
  - export content

> This environment does not have Vercel/Render/Railway credentials or CLI access, so the live external deployment itself must be executed from a machine or CI pipeline with provider login.
