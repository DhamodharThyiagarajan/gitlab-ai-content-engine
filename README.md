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

## Current completion status

The project is prepared for provider setup, but it is not publicly deployed. The backend workflow, Firebase authentication, role checks, document extraction, review gates, and Markdown export are implemented. Automated tests cover project contracts, extraction behavior, source-reference fallback, and profile-role escalation; the production frontend build includes all app routes.

Public URLs, live PostgreSQL, Firebase provider configuration, and a demo recording still require external accounts and credentials.

## Project structure

```text
├── README.md
├── .env.example
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   ├── hooks/
│   │   └── lib/
│   ├── content-editor/
│   ├── review-panel/
│   ├── styles/
├── backend/
│   └── app/
│       ├── api/
│       ├── auth/
│       ├── db/
│       ├── models/
│       ├── orchestration/
│       ├── publishing/
│       └── services/
├── ai/
│   ├── agents/
│   │   ├── context_reader/
│   │   ├── documentation_writer/
│   │   ├── technical_reviewer/
│   │   ├── tone_optimizer/
│   │   └── publishing_coordinator/
│   ├── prompts/
│   ├── schemas/
│   ├── retrieval/
│   └── evaluation/
├── data/
│   ├── sample_inputs/
│   ├── sample_docs/
│   ├── style_guides/
│   └── content_templates/
├── docs/
│   ├── architecture.md
│   ├── api_documentation.md
│   ├── workflow_states.md
│   ├── demo_script.md
│   └── screenshots/
├── tests/
│   ├── functional_tests/
│   ├── ai_output_tests/
│   ├── security_tests/
│   └── edge_cases/
├── deployment/
│   ├── vercel_notes.md
│   ├── backend_deployment.md
│   └── environment_setup.md
└── sample/
```

The root frontend feature folders and top-level backend folders are organizational guides; executable code lives under `frontend/src/` and `backend/app/`. The empty `frontend/app` placeholder was removed because Next.js prioritizes it over `src/app`, which previously caused a build to omit all app routes.

Prior-document retrieval is not connected to the runtime workflow. Drafts use each job's supplied sources and preserve source references. The workflow calculates a heuristic quality score and requires human approval before export; this score is advisory, not a factuality guarantee.

## Quick start

### Backend
```bash
cd backend
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows: .venv\\Scripts\\activate
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

For local development, use `DATABASE_URL=sqlite:///./gitlab_ai_content.db` and `AI_PROVIDER=mock`. Configure Firebase Admin credentials and PostgreSQL for production. Copy `frontend/.env.example` to `frontend/.env.local`, set the Firebase public values and `NEXT_PUBLIC_BACKEND_URL`, then open http://localhost:3000. New Firebase users receive the `writer` role; an administrator grants elevated roles.

Docker Compose exposes the frontend at `http://localhost:5173` and configures backend CORS for that origin. Firebase client and Admin credentials are still required to use authenticated flows.

For real AI, set `AI_PROVIDER=openai_compatible` and `OPENAI_API_KEY` in `.env`.

## API
- POST /api/auth/verify
- POST /api/auth/sync-user
- PUT /api/auth/profile
- GET /api/auth/me
- GET /api/auth/users (admin)
- PUT /api/auth/users/{user_id}/role (admin)
- POST /api/content-jobs
- POST /api/content-jobs/upload
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

See [docs/api_documentation.md](docs/api_documentation.md) for the current API surface and [deployment/README.md](deployment/README.md) for the public-host setup checklist.

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

Open `http://localhost:3000`.
