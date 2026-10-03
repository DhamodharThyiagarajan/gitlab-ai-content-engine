# API documentation

Base URL: `http://localhost:8000` (local) or your deployed backend URL. Interactive docs: `/docs` (Swagger UI).
All `/api/*` routes require `Authorization: Bearer <Firebase ID token>`. Roles are assigned server-side (`writer`, `reviewer`, `approver`, `admin`).

| Method | Path | Roles | Purpose |
| --- | --- | --- | --- |
| GET | `/health`, `/health/ready` | public | Liveness / database readiness |
| POST | `/api/auth/verify`, `/api/auth/sync-user` | any | Verify token and sync the profile |
| GET | `/api/auth/me` | any | Current user and role |
| PUT | `/api/auth/profile` | any | Update display name (role is ignored) |
| GET | `/api/auth/users` | admin | List users |
| PUT | `/api/auth/users/{id}/role` | admin | Assign a role |
| POST | `/api/content-jobs` | writer, admin | Create a content job from pasted text |
| POST | `/api/content-jobs/upload` | writer, admin | Create a job from PDF/DOCX/TXT/MD/CSV (multipart) |
| GET | `/api/content-jobs` | any | List jobs (writers see their own) |
| GET | `/api/content-jobs/{id}` | any | Job detail: drafts, versions, review data |
| POST | `/api/context-pack` | writer, admin | Body `{"job_id": 1}`. Build the structured context pack (facts, gaps, contradictions, source refs, retrieved knowledge) without drafting |
| POST | `/api/content-jobs/{id}/run` | writer, admin | Run the multi-agent workflow. `422` if the source is too thin |
| GET | `/api/content-jobs/{id}/audit` | reviewer, approver, admin | Audit trail for the job |
| POST | `/api/drafts/{id}/review` | reviewer, approver, admin | Body `{"decision": "approve\|reject\|request_revision", "comments": ""}`. Only approver/admin may approve |
| POST | `/api/drafts/{id}/refine` | writer, reviewer, admin | Body `{"stage": "full\|tone\|structure\|clarity\|technical", "comments": ""}`. Reruns only the selected stage and creates a new version |
| POST | `/api/drafts/{id}/edit` | writer, reviewer, admin | Body `{"content": "..."}`. Human edit saved as a new version; approval restarts |
| GET | `/api/drafts/{id}/diff/{other_id}` | any | Unified diff between two versions of a job |
| POST | `/api/publish/export` | approver, admin | Body `{"draft_id": 1, "format": "markdown\|cms_json", "create_merge_request": false}`. `409` unless the draft is approved |
| GET | `/api/metrics` | any | Throughput, pipeline, quality, rework rate, approval cycle time, error rate |

## Error model
| Status | Meaning |
| --- | --- |
| 400 | Invalid input (empty/unsupported file, bad decision or stage, empty edit) |
| 401 | Missing or invalid Firebase token |
| 403 | Role does not allow the action, or writer accessing another writer's job |
| 404 | Job or draft not found |
| 409 | Export attempted on an unapproved draft |
| 422 | Validation error, or insufficient source context for drafting |
| 502 | AI workflow failure (job is marked `failed`, state preserved, can be retried) |

## Structured output (per draft)
`technical_review` contains: `verdict`, `risks`, `unsupported_claims`, `missing_information`/`context_gaps`, `supported_information` (fact + source refs), `source_refs`, `quality_score`, `evidence_count`, `prompt_version`, `orchestrator`, `human_approval_required`.
