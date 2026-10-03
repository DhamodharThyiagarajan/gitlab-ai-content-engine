# GitLab AI Content & Documentation Engine

A governed, multi-agent content production platform that turns technical change (code/MR notes, release updates, API changes, briefs, uploaded documents) into **review-ready, source-grounded** release notes, documentation, developer blogs, API references and onboarding guides - with human approval before anything is published.

| | |
| --- | --- |
| **Deployed app** | `<ADD YOUR DEPLOYED FRONTEND URL HERE>` |
| **Backend API / docs** | `<ADD YOUR DEPLOYED BACKEND URL>/docs` |
| **Demo video** | `<ADD GOOGLE DRIVE LINK - "Anyone with the link can view">` |
| **Repository** | `<ADD REPO URL>` |

## Product overview
GitLab ships faster than documentation can keep up. This engine closes the gap without removing accountability:

1. **Intake** - choose content type, audience, product area and channel; paste text or upload PDF/DOCX/TXT/MD/CSV.
2. **Context pack** - sources are normalized into facts, gaps, contradictions and source references. Thin or empty input is rejected before any drafting.
3. **Multi-agent workflow (CrewAI)** - Context Reader -> Documentation Writer -> Technical Reviewer -> Tone Optimizer -> Publishing Coordinator.
4. **Governed review** - source panel, quality score, unsupported-claim flags, version history and diff, manual edit, stage-level reruns (tone / structure / clarity / technical).
5. **Approval gate** - reviewers request revisions; only approvers/admins approve; export is blocked (`409`) until approved.
6. **Publish** - Markdown with front matter, CMS-ready JSON, optional GitLab merge request.
7. **Operations dashboard** - throughput, pipeline, quality, rework rate, approval cycle time, error rate.

## How reliability and safety are handled
- **Source grounding**: the writer may use only the context pack; every draft ends with source references.
- **Deterministic grounding guard** (runs with any model): versions, API paths and metrics in the draft that do not appear in the source are flagged as unsupported claims.
- **Visible failure**: errors mark the job `failed`, keep state, and can be retried. Input problems return clear 4xx errors.
- **Audit trail**: job creation, workflow runs (agent trace, timings, prompt version, orchestrator), reviews, edits, refinements and exports are logged.
- **Backend-only secrets** and role-based access (writer / reviewer / approver / admin). Roles cannot be set from the client.
- **Mock AI mode** (`AI_PROVIDER=mock`) runs the entire workflow offline and deterministically. If CrewAI fails with a real model, the same five agents run through a direct pipeline automatically.

## Architecture
See [`docs/architecture.md`](docs/architecture.md). In short: Next.js + Firebase Auth -> FastAPI -> SQLAlchemy (SQLite locally, PostgreSQL/Supabase in production) -> ContentWorkflow (Chroma retrieval over job sources and approved knowledge, CrewAI agents, versioned prompts, grounding guard) -> OpenAI-compatible LLM.

```
backend/   app/ (API, auth, models, services)   ai/ (agents, prompts/v1, schemas, retrieval, workflow)
frontend/  src/app (intake, review, dashboard, analytics, auth)
data/      sample_inputs/  sample_docs/  style_guides/  content_templates/
docs/      architecture.md  api_documentation.md  workflow_states.md  demo_script.md  screenshots/
tests/     functional_tests/  ai_output_tests/  security_tests/  edge_cases/
deployment/ vercel_notes.md  backend_deployment.md  environment_setup.md
```

## Quick start
Full instructions, including Firebase and role setup: [`deployment/environment_setup.md`](deployment/environment_setup.md).

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
cp ../.env.example .env                                   # set Firebase values; AI_PROVIDER=mock works without a key
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
cp ../.env.example .env.local                             # NEXT_PUBLIC_* values
npm install && npm run dev                                # http://localhost:3000

# Tests (no cloud credentials needed)
cd backend && python -m pytest ../tests -q
```
Docker: `docker compose up --build` (reads the root `.env`; build context is the repo root).

## AI workflow
| Agent | Responsibility | Prompt |
| --- | --- | --- |
| Context Reader | Facts, gaps, contradictions, source refs | `backend/ai/prompts/v1/context_reader.md` |
| Documentation Writer | First draft from approved context + style guide + template | `.../documentation_writer.md` |
| Technical Reviewer | Claim-by-claim check against evidence | `.../technical_reviewer.md` |
| Tone Optimizer | Audience/channel voice, no new facts | `.../tone_optimizer.md` |
| Publishing Coordinator | Clean customer-facing Markdown | `.../publishing_coordinator.md` |

Prompts are versioned files (`PROMPT_VERSION` is logged on every run). Style rules and structure per content type live in `data/style_guides` and `data/content_templates`.

Real AI: set `AI_PROVIDER=openai_compatible`, `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL` (any OpenAI-compatible endpoint, including Gemini's).

## API
Summary below; full reference in [`docs/api_documentation.md`](docs/api_documentation.md).

`POST /api/content-jobs` | `POST /api/content-jobs/upload` | `POST /api/context-pack` | `POST /api/content-jobs/{id}/run` | `GET /api/content-jobs[/{id}]` | `GET /api/content-jobs/{id}/audit` | `POST /api/drafts/{id}/review` | `POST /api/drafts/{id}/refine` | `POST /api/drafts/{id}/edit` | `GET /api/drafts/{id}/diff/{other}` | `POST /api/publish/export` | `GET /api/metrics` | `GET /health`, `/health/ready`

## Screenshots
Add screenshots to `docs/screenshots/` and reference them here:

| Intake | Workflow result | Review | Dashboard |
| --- | --- | --- | --- |
| `docs/screenshots/intake.png` | `docs/screenshots/workflow.png` | `docs/screenshots/review.png` | `docs/screenshots/dashboard.png` |

## Demonstration
Follow [`docs/demo_script.md`](docs/demo_script.md). Sample inputs for a release note, documentation page, developer blog, API reference and onboarding guide are in `data/sample_inputs/`.

## Team contribution
| Member | Role | Contribution |
| --- | --- | --- |
| `<name>` | `<e.g. Product & frontend>` | `<what you built>` |
| `<name>` | `<e.g. Backend & API>` | `<what you built>` |
| `<name>` | `<e.g. AI workflow & prompts>` | `<what you built>` |
| `<name>` | `<e.g. Testing, deployment, docs>` | `<what you built>` |

## References
CrewAI, FastAPI, Next.js, Firebase Authentication, ChromaDB, GitLab API (merge request publishing), Vercel, Render.
