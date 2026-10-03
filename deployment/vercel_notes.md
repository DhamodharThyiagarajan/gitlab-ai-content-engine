# Frontend deployment (Vercel)

1. Import the repo in Vercel. **Root Directory: `frontend`**. Framework: Next.js.
2. Environment variables (Production):
   - `NEXT_PUBLIC_BACKEND_URL` = deployed backend URL (no trailing slash)
   - `NEXT_PUBLIC_FIREBASE_API_KEY`, `_AUTH_DOMAIN`, `_PROJECT_ID`, `_STORAGE_BUCKET`, `_MESSAGING_SENDER_ID`, `_APP_ID`
3. Deploy, then add the Vercel domain to Firebase **Authorized domains** and to the backend `CORS_ORIGINS`.
4. Smoke test: sign up, create a job, run the workflow, review, approve (as approver), publish.
