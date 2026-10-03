# Environment Setup Guide

Use this file to prepare your local and production environment for both the backend and frontend.

## 1) Backend local setup

```bash
cd backend
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the `backend` folder using the values from [.env.example](../.env.example).

Example:

```env
APP_NAME=GitLab AI Content Engine
APP_ENV=development
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
FRONTEND_URL=http://localhost:3000
DATABASE_URL=sqlite:///./data/app.db
AUTH_PROVIDER=firebase
FIREBASE_PROJECT_ID=your-firebase-project-id
JWT_SECRET=change-me
AI_PROVIDER=mock
CORS_ORIGINS=http://localhost:3000
```

Run the backend:

```bash
uvicorn app.main:app --reload --port 8000
```

## 2) Frontend local setup

```bash
cd frontend
npm install
```

Create a `.env.local` file in `frontend`:

```env
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_FIREBASE_API_KEY=your_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-project-id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your-project.firebasestorage.app
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id
```

Run the frontend:

```bash
npm run dev
```

Open:

```text
http://localhost:3000
```

## 3) Production environment values

For Render and Vercel, use production versions of the same settings.

### Render backend values

```env
FRONTEND_URL=https://your-vercel-app.vercel.app
DATABASE_URL=postgresql+psycopg://user:password@host:5432/dbname
CORS_ORIGINS=https://your-vercel-app.vercel.app
AI_PROVIDER=mock
```

### Vercel frontend values

```env
NEXT_PUBLIC_BACKEND_URL=https://your-render-service.onrender.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-firebase-project-id
NEXT_PUBLIC_FIREBASE_API_KEY=your_firebase_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your-project.firebasestorage.app
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id
```

## 4) Secrets and security

- Never commit `.env` files to GitHub.
- Put real secrets in Render and Vercel environment variables.
- Keep Firebase project IDs and API keys consistent across both apps.
- Use Postgres for production instead of SQLite.

## 5) Deployment checklist

Before going live, confirm:

- [ ] backend deployed on Render
- [ ] frontend deployed on Vercel
- [ ] `NEXT_PUBLIC_BACKEND_URL` is correct
- [ ] `CORS_ORIGINS` includes Vercel URL
- [ ] Firebase config is correct
- [ ] database is PostgreSQL
- [ ] health endpoint responds successfully

## 6) Example final configuration

```env
NEXT_PUBLIC_BACKEND_URL=https://gitlab-ai-content-engine-api.onrender.com
CORS_ORIGINS=https://gitlab-ai-content-engine.vercel.app
```

This is the typical production setup for this repo.
