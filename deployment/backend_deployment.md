# Backend deployment (Render or Railway)

The backend needs the repository root because it ships `data/` (style guides, templates, approved docs) with the code.

## Render (Docker)
1. New > **Web Service** > connect the repo. Runtime: **Docker**. Dockerfile path: `backend/Dockerfile`. Docker build context / root directory: repository root (`.`).
2. Health check path: `/health`.
3. Environment variables: everything in `.env.example` marked backend (see `environment_setup.md`). Set `CORS_ORIGINS` to your frontend URL, `DATABASE_URL` to a PostgreSQL URL (Supabase/Render Postgres; use `postgresql+psycopg://...`), and `FIREBASE_SERVICE_ACCOUNT_JSON`.
4. Add a persistent disk mounted at `/app/data` if you keep SQLite or Chroma data; with PostgreSQL only Chroma and uploads use the disk. Without a disk, data resets on each deploy.

## Render/Railway without Docker
Root directory: repo root. Build: `pip install -r backend/requirements.txt`. Start: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`.

## Notes
- CrewAI and ChromaDB make the image large and the first build slow (several minutes). Use at least 1 GB RAM. If you need a lighter deployment, remove CrewAI usage by setting `USE_CREWAI=false` (the direct agent pipeline runs the same five agents).
- Verify after deploy: open `<backend-url>/health/ready` and `<backend-url>/docs`.
