# GitLab AI Content & Documentation Engine

A full-stack, source-grounded content production platform based on the supplied GitLab AI Content & Documentation Engine specification and the existing repository structure.

## What is implemented
- Firebase Authentication with backend-verified ID tokens and backend-managed roles: writer, reviewer, approver, admin
- Content job intake for release notes, docs, blogs, onboarding guides, and API references
- Source/context normalization
- Multi-stage AI workflow: context reader -> documentation writer -> technical reviewer -> tone optimizer -> publishing coordinator
- Mock AI mode for zero-key local demos
- OpenAI-compatible provider through environment variables
- Draft/version history and reviewer decisions
- Quality/risk flags and source references
- Markdown export with approval gate
- Operations metrics
- React dashboard, intake, jobs, draft review and metrics views
- Supabase PostgreSQL via `DATABASE_URL`; SQLite remains available for local development
- Docker Compose for local full-stack startup

## Quick start

### Backend
```bash
cd backend
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Configure the Firebase Admin credentials and Supabase `DATABASE_URL` in `backend/.env`. Set the frontend's `NEXT_PUBLIC_BACKEND_URL` to the FastAPI URL. Open http://localhost:3000. For local JWT demo accounts, set `AUTH_PROVIDER=legacy` explicitly; Firebase is the default and new Firebase accounts receive the `writer` role.

Legacy demo accounts (available only when `AUTH_PROVIDER=legacy`):
- writer@example.com / password123
- reviewer@example.com / password123
- approver@example.com / password123
- admin@example.com / password123

For real AI, set `AI_PROVIDER=openai_compatible` and `OPENAI_API_KEY` in `.env`.

## API
- POST /api/auth/register
- POST /api/auth/login
- GET /api/auth/me
- POST /api/content-jobs
- GET /api/content-jobs
- GET /api/content-jobs/{job_id}
- POST /api/content-jobs/{job_id}/run
- POST /api/drafts/{draft_id}/review
- POST /api/drafts/{draft_id}/refine
- POST /api/publish/export
- GET /api/metrics
- GET /health

## Architecture
See `docs/architecture.md`, `docs/workflow_states.md`, and `docs/demo_script.md`.

The supplied specification calls for source grounding, specialized agents, human approval, auditability, retrieval-ready knowledge assets, exports, and deployment configuration; this implementation includes those core paths. fileciteturn0file0L106-L166

## Document ingestion and real agent workflow

This implementation keeps the original repository structure and adds document ingestion inside the existing `backend/app/services`, `backend/app/api`, and `backend/app/orchestration` modules.

### Supported uploads

- PDF (text-based PDFs; page-level source markers are preserved)
- DOCX
- TXT
- Markdown
- CSV

Scanned/image-only PDFs require OCR and are rejected with an explicit message rather than silently producing empty context.

### Workflow

`Upload -> Document Extraction -> Context Reader -> Documentation Writer -> Technical Reviewer -> Tone Optimizer -> Publishing Coordinator -> Human Review -> Export`

The Context Reader creates an evidence map containing facts, changes, requirements, entities, gaps, contradictions, and source references. PDF evidence is marked with the original filename and page number.

### Real AI configuration

Copy `.env.example` to `.env` and configure:

```env
AI_PROVIDER=openai_compatible
OPENAI_API_KEY=your_key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4.1-mini
AI_TIMEOUT_SECONDS=120
```

`AI_PROVIDER=mock` remains available for offline UI/API testing. In mock mode, document extraction still runs locally, but model-based reasoning is replaced by deterministic fallback output.

### Backend dependencies

```powershell
cd backend
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.
