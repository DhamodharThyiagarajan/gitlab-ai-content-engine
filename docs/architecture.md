# Architecture

The Next.js frontend authenticates users with Firebase Authentication and sends Firebase ID tokens to FastAPI. FastAPI verifies tokens, enforces role permissions, and persists application data through SQLAlchemy. Set `DATABASE_URL` to a Supabase PostgreSQL connection string to use Supabase as the application database; SQLite remains available for local development.

Firebase stores identities. The relational database stores application profiles, content jobs, context packs, drafts, reviews, audit events, and metrics data. New Firebase accounts receive the `writer` role. Client supplied roles are ignored; elevated roles must be granted through a trusted administrative process.

The governed workflow separates context preparation, drafting, technical review, tone refinement, publishing preparation, human review, and Markdown export.

## Role permissions

| Role | Create and run jobs | View jobs | Refine drafts | Request revisions | Approve | Publish | Manage roles |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Writer | Yes | Own jobs | Own drafts | — | — | — | — |
| Reviewer | — | All jobs | Yes | Yes | — | — | — |
| Approver | — | All jobs | — | Yes | Yes | Yes | — |
| Admin | Yes | All jobs | Yes | Yes | Yes | Yes | Yes |

The API enforces these permissions. Admins manage assignments through `GET /api/auth/users` and `PUT /api/auth/users/{user_id}/role`; a first admin must be assigned directly in the trusted database setup because account signup always creates a writer.

## Configuration

- Set `FIREBASE_PROJECT_ID` in the backend environment.
- Provide Firebase Admin credentials through `FIREBASE_SERVICE_ACCOUNT_JSON` or Application Default Credentials.
- Set `DATABASE_URL` to the Supabase PostgreSQL URI. Install backend requirements to include the PostgreSQL driver.
- Set `NEXT_PUBLIC_BACKEND_URL` to the FastAPI base URL in the frontend environment.
- Set `CORS_ORIGINS` to the frontend origin(s).
