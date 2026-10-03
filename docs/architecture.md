# Architecture

```
Next.js (Firebase Auth)  --Bearer ID token-->  FastAPI  --> SQLAlchemy (SQLite / PostgreSQL / Supabase)
                                                  |
                                                  +--> ContentWorkflow
                                                        |-- Retrieval: Chroma (job chunks + style guides, templates, approved docs)
                                                        |-- CrewAI crew: Context Reader -> Writer -> Technical Reviewer -> Tone -> Publisher
                                                        |-- Direct agent pipeline (mock mode / automatic fallback)
                                                        |-- Grounding guard (versions, API paths, metrics must exist in source)
                                                        +-- LLM: OpenAI-compatible API, or deterministic mock
```

## Layers
| Layer | Location |
| --- | --- |
| Frontend (intake, workflow, review, dashboard) | `frontend/src/app` |
| API, auth, roles, audit | `backend/app` |
| Agents | `backend/ai/agents/*` and `backend/ai/agents/crew.py` |
| Versioned prompts | `backend/ai/prompts/v1/*.md` (`PROMPT_VERSION` is stored in every audit event) |
| Schemas | `backend/ai/schemas`, `technical_review` payload in `ai/common.py` |
| Retrieval and knowledge | `backend/ai/retrieval`, `data/style_guides`, `data/content_templates`, `data/sample_docs` |
| Publishing adapters | `backend/app/api/publishing.py`, `backend/app/services/gitlab_publisher.py` |
| Tests | `tests/` |

## Governance
- Backend-only secrets (LLM key, Firebase Admin, GitLab token). The browser only has the public Firebase web config.
- Role-based access: writer creates/runs, reviewer comments/requests revision, approver/admin approves and publishes, admin manages roles. Roles are never accepted from the client.
- Human approval gate: export returns `409` unless the draft is approved. Edits and refinements create new versions and restart approval.
- Every job, workflow run (agents, timings, prompt version), review, edit, refinement and export is written to `audit_events`.
- Failures are visible: failed jobs keep state, show an error and can be retried; thin source input is rejected with `422`.

## Role permissions
| Role | Create/run | View | Refine/edit | Request revision | Approve | Publish | Manage roles |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Writer | Yes | Own jobs | Own drafts | - | - | - | - |
| Reviewer | - | All | Yes | Yes | - | - | - |
| Approver | - | All | - | Yes | Yes | Yes | - |
| Admin | Yes | All | Yes | Yes | Yes | Yes | Yes |

## Configuration
See `deployment/environment_setup.md` and `.env.example`.
