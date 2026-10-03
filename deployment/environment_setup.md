# Environment setup

## 1. Firebase (authentication)
1. Create a project at https://console.firebase.google.com and enable **Authentication > Email/Password**.
2. Project settings > General > *Your apps* > add a **Web app**. Copy the config into `NEXT_PUBLIC_FIREBASE_*`.
3. Project settings > Service accounts > **Generate new private key**. Put the JSON, as a single line, in `FIREBASE_SERVICE_ACCOUNT_JSON` on the backend (never commit it). Set `FIREBASE_PROJECT_ID` to the same project.
4. Authentication > Settings > Authorized domains: add your deployed frontend domain.

## 2. First admin / demo roles
New accounts are `writer`. Sign up three or four users in the app, then set roles directly in the database once:
```sql
UPDATE users SET role='admin'    WHERE email='you@example.com';
UPDATE users SET role='reviewer' WHERE email='reviewer@example.com';
UPDATE users SET role='approver' WHERE email='approver@example.com';
```
SQLite: `sqlite3 backend/data/app.db`. After the first admin exists, roles can be managed with `PUT /api/auth/users/{id}/role`.

## 3. AI provider
- `AI_PROVIDER=mock` works with no key (deterministic, source-grounded output - good for tests and backup demos).
- Real AI: `AI_PROVIDER=openai_compatible`, `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL`. Any OpenAI-compatible endpoint works (for example Gemini's OpenAI-compatible URL `https://generativelanguage.googleapis.com/v1beta/openai/` with a Gemini model name).
- `USE_CREWAI=true` runs the five agents through CrewAI; if CrewAI fails the direct pipeline is used automatically.

## 4. Optional GitLab merge request publishing
Set `GITLAB_URL`, `GITLAB_TOKEN` (scope `api`), `GITLAB_PROJECT_ID`. Export with `create_merge_request: true` commits `docs/<file>.md` on branch `content-engine/job-<id>` and opens an MR.

## 5. Local run and tests
```bash
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
cp ../.env.example .env        # edit it
uvicorn app.main:app --reload --port 8000
# in another terminal
cd frontend && cp ../.env.example .env.local   # keep NEXT_PUBLIC_* values; npm install; npm run dev
# tests (no cloud credentials needed)
cd backend && python -m pytest ../tests -q
```
