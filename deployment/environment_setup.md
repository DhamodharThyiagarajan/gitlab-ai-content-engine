# Environment setup

## Local setup
1. Create a Python virtual environment
2. Install backend requirements
3. Install frontend dependencies
4. Copy `.env.example` and fill in secrets
5. Run the backend and frontend locally

## Production setup
- Set Vercel `NEXT_PUBLIC_BACKEND_URL` to the deployed backend origin.
- Set backend `FRONTEND_URL` and `CORS_ORIGINS` to the exact Vercel origin.
- Set backend `DATABASE_URL` to a PostgreSQL SQLAlchemy URL (Supabase direct connection URI, not its REST URL).
- Set `FIREBASE_PROJECT_ID` and either `FIREBASE_SERVICE_ACCOUNT_JSON` or application-default credentials.
- Use `AI_PROVIDER=mock` for a credential-free deployment, or configure `openai_compatible` and `OPENAI_API_KEY`.
- Keep credentials in provider secret settings; never commit `.env` files or service-account JSON.
- Verify `/health`, then test signup/login, content creation, review, and export against the public services.
