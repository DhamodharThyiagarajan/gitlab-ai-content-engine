# API documentation

The FastAPI service publishes interactive OpenAPI documentation at `/docs` and its schema at `/openapi.json` when running locally or in the deployed backend.

## Authentication

- The frontend signs users in with Firebase Authentication.
- Protected API requests send the Firebase ID token as `Authorization: Bearer <token>`.
- New Firebase identities receive the `writer` role. Elevated roles must be assigned through a trusted admin process.
- The API returns `401` for missing or invalid credentials and `403` when an authenticated user lacks the required role.

## Core endpoints

### Authentication
- `POST /api/auth/verify`
- `POST /api/auth/sync-user`
- `PUT /api/auth/profile`
- `GET /api/auth/me`
- `GET /api/auth/users` (admin)
- `PUT /api/auth/users/{user_id}/role` (admin)

### Content jobs
- `POST /api/content-jobs`
- `POST /api/content-jobs/upload`
- `GET /api/content-jobs`
- `GET /api/content-jobs/{job_id}`
- `POST /api/content-jobs/{job_id}/run`

### Reviews and approval
- `POST /api/drafts/{draft_id}/review`
- `POST /api/drafts/{draft_id}/refine`

### Publishing and metrics
- `POST /api/publish/export`
- `GET /api/metrics`
- `GET /health`

## Notes

- Writers can create and run only their own jobs.
- Reviewers can inspect jobs and provide feedback.
- Approvers control publication approval flows.
- Profile updates cannot change roles; role assignments use the admin-only role endpoint.
- The app should always keep source references with generated drafts.
