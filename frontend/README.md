# Frontend Deployment Guide for Netlify

This frontend is a Next.js app for the GitLab AI Content Engine. It calls the Python FastAPI backend and uses Firebase client configuration.

## Local development

```bash
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:3000
```

Create a `.env.local` file in the `frontend` folder:

```env
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_FIREBASE_API_KEY=your_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-project-id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your-project.firebasestorage.app
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id
```

## Deploy on Netlify

### 1) Prepare the backend first

Your frontend talks to the backend API through `NEXT_PUBLIC_BACKEND_URL`, so the backend should already be deployed and reachable.

Recommended setup:
- Backend hosted on Render
- Frontend hosted on Netlify

Example backend URL:

```text
https://gitlab-ai-content-engine-api.onrender.com
```

### 2) Push the repo to GitHub

Make sure the project is in a GitHub repository.

### 3) Import project in Netlify

1. Open https://app.netlify.com
2. Click “Add new site” → “Import an existing project”
3. Connect your GitHub repository
4. Set the project root to:
   - Base directory: `frontend`
   - Build command: `npm run build`
   - Publish directory: `.next`

### 4) Add environment variables in Netlify

In Netlify → Site settings → Environment variables, add:

```env
NEXT_PUBLIC_BACKEND_URL=https://your-render-backend.onrender.com
NEXT_PUBLIC_FIREBASE_API_KEY=your_firebase_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-project-id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your-project.firebasestorage.app
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id
```

### 5) Deploy

Click “Deploy site”. Netlify will run the Next.js build and publish the site.

## Netlify + Next.js note

This app is a Next.js app with server/client runtime behavior and environment variables. Netlify supports Next.js deployments through the Netlify Next.js runtime or the official Next integration. If you are using the standard Netlify deployment flow for Next.js, make sure the project is set up with the proper Next integration and your deployment settings match the app structure.

## Backend CORS configuration

Because the frontend is hosted on a different domain, the backend must allow your Netlify domain in `CORS_ORIGINS`.

Example on Render:

```env
CORS_ORIGINS=https://your-app-name.netlify.app
```

If you are using localhost during local testing, include it too:

```env
CORS_ORIGINS=http://localhost:3000,https://your-app-name.netlify.app
```

## Production example

Example final setup:

```env
NEXT_PUBLIC_BACKEND_URL=https://gitlab-ai-content-engine-api.onrender.com
CORS_ORIGINS=https://gitlab-ai-content-engine.netlify.app
```

## Useful checks after deployment

1. Open the Netlify site URL
2. Confirm the app loads
3. Sign in or test the dashboard
4. Confirm API calls are reaching the Render backend
5. Check browser console for CORS or Firebase errors

## Common issues

### CORS error

This happens when the Netlify domain is not added to the backend allowlist.

### API calls fail

Check that `NEXT_PUBLIC_BACKEND_URL` points to the Render backend URL and not to the Netlify frontend URL.

### Firebase login fails

Make sure all `NEXT_PUBLIC_FIREBASE_*` values match the same Firebase project you configured in the backend.

## Recommended final architecture

- Frontend: Netlify
- Backend: Render
- Database: PostgreSQL
- Auth: Firebase

This is the recommended deployment pattern for this project.
