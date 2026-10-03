# Vercel Deployment Guide

This project’s frontend is a Next.js app in the `frontend` folder. The app expects `NEXT_PUBLIC_BACKEND_URL` and Firebase client values to be set in the deployment environment.

## 1) Deploy the backend first

For this app, the backend should be running before the frontend is tested in production.

Recommended flow:

1. Deploy the backend to Render
2. Confirm the backend health endpoint works
3. Deploy the frontend to Vercel
4. Set the frontend env vars
5. Add the Vercel domain to backend CORS

## 2) Frontend entry point

The app should open the login screen first. The site root should redirect to `/login`.

The frontend application uses the `/login` route as its default landing page, while the backend stays on its own Render URL.

## 3) Backend URL to use in the frontend

Your frontend will call the backend through the value in `NEXT_PUBLIC_BACKEND_URL`.

Example:

```env
NEXT_PUBLIC_BACKEND_URL=https://your-render-backend.onrender.com
```

Do not set this to your Vercel URL. It must point to the backend service.

## 4) Import the repo into Vercel

1. Open https://vercel.com
2. Click “Add New Project”
3. Import your GitHub repository
4. Set the root directory to `frontend`
5. Framework preset should be detected as Next.js automatically
6. Build command:

```bash
npm run build
```

7. Output directory:

```text
.next
```

## 5) Add environment variables in Vercel

In Vercel → Project → Settings → Environment Variables, add:

```env
NEXT_PUBLIC_BACKEND_URL=https://your-render-backend.onrender.com
NEXT_PUBLIC_FIREBASE_API_KEY=your_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-project-id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your-project.firebasestorage.app
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id
```

## 6) Add the Vercel URL to backend CORS

After the frontend is deployed, copy the live Vercel URL and add it to the backend environment on Render.

Example:

```env
CORS_ORIGINS=https://your-project.vercel.app
```

If you also want localhost support while developing:

```env
CORS_ORIGINS=http://localhost:3000,https://your-project.vercel.app
```

## 7) Recommended backend env values for Render

These are the variables the backend service should have in Render:

```env
APP_NAME=GitLab AI Content Engine
APP_ENV=production
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
FRONTEND_URL=https://your-project.vercel.app
DATABASE_URL=postgresql+psycopg://user:password@host:5432/dbname
AUTH_PROVIDER=firebase
FIREBASE_PROJECT_ID=your-firebase-project-id
JWT_SECRET=your-long-random-secret
JWT_EXPIRE_MINUTES=1440
AI_PROVIDER=openai_compatible
OPENAI_API_KEY=your_key
OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
OPENAI_MODEL=gemini-3.1-flash-lite
AI_TIMEOUT_SECONDS=120
CORS_ORIGINS=https://your-project.vercel.app
```

## 8) Production example

```env
NEXT_PUBLIC_BACKEND_URL=https://gitlab-ai-content-engine-api.onrender.com
CORS_ORIGINS=https://gitlab-ai-content-engine.vercel.app
```

## 9) Final verification

After deployment:

1. Open the Vercel live URL
2. Confirm the dashboard loads
3. Confirm login works
4. Confirm API calls reach the Render backend
5. Check browser console for CORS or Firebase issues

## 10) Common issues

### CORS error

The Vercel domain is missing from the backend allowlist.

### API calls fail

`NEXT_PUBLIC_BACKEND_URL` points to the wrong host, usually the frontend URL instead of the backend URL.

### Firebase login fails

The Firebase values do not match the same project used by the backend.

## 11) Recommended architecture

- Frontend: Vercel
- Backend: Render
- Database: PostgreSQL
- Authentication: Firebase

This is the recommended deployment setup for this app.
