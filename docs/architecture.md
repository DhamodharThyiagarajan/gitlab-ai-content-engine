# Architecture

The project uses a full-stack architecture with a Next.js frontend and a FastAPI backend.

The **Next.js frontend** handles the user interface and authentication through **Firebase Authentication**. After login, Firebase provides an ID token, which is sent to the FastAPI backend. FastAPI verifies the token, checks the user's role and permissions, and handles application requests.

The backend uses **SQLAlchemy** for database interaction. **SQLite** is used by default for local development, while a PostgreSQL connection can be configured through `DATABASE_URL` for Supabase or another shared database.

Firebase manages user identities, while the relational database stores application data such as user profiles, content jobs, context packs, drafts, reviews, audit events, and metrics.

When a new user signs up, the default role is `writer`. Client-provided roles are not trusted. Higher-level roles such as `reviewer`, `approver`, and `admin` must be assigned through the authorized role-management API.

The governed workflow separates the major stages of the documentation process:

**Context Preparation → Drafting → Technical Review → Tone Refinement → Publishing Preparation → Human Review → Markdown Export**

## Role Permissions

| **Role** | **Create & Run Jobs** | **View Jobs** | **Refine Drafts** | **Request Revisions** | **Approve** | **Publish** | **Manage Roles** |
|---|---|---|---|---|---|---|---|
| Writer | Yes | Own jobs | Own drafts | — | — | — | — |
| Reviewer | — | All jobs | Yes | Yes | — | — | — |
| Approver | — | All jobs | — | Yes | Yes | Yes | — |
| Admin | Yes | All jobs | Yes | Yes | Yes | Yes | Yes |

These permissions are enforced by the backend API.

Admins can manage user roles through:

- `GET /api/auth/users`
- `PUT /api/auth/users/{user_id}/role`

A first admin must be assigned directly through the trusted database setup because newly created accounts are assigned the `writer` role by default.

## Configuration

The following environment variables are required for different parts of the application:

- `FIREBASE_PROJECT_ID` — Firebase project ID used by the backend.
- `FIREBASE_SERVICE_ACCOUNT_JSON` — Firebase Admin credentials, or Application Default Credentials can be used.
- `DATABASE_URL` — Database connection string. It defaults to `sqlite:///./data/app.db` for local development and can be changed to a PostgreSQL URI for Supabase or another shared database.
- Firebase web app configuration — Matching Firebase project values must be configured for the frontend and backend.
- `NEXT_PUBLIC_BACKEND_URL` — FastAPI backend URL used by the frontend.
- `CORS_ORIGINS` — Allowed frontend origins, such as `http://localhost:3000` during local development.
- `AI_PROVIDER` — Set to `mock` for local testing without an AI API key, or `openai_compatible` to use an OpenAI-compatible AI provider.
- `OPENAI_BASE_URL` — Base URL of the OpenAI-compatible provider.
- `OPENAI_MODEL` — AI model to use.
- `OPENAI_API_KEY` — API key for the configured AI provider.

## High-Level Architecture

The overall flow can be summarized as:

**User → Next.js Frontend → Firebase Authentication → FastAPI Backend → Database / AI Workflow → Human Review → Markdown Export**

This architecture separates authentication, application logic, data persistence, AI processing, and human approval into clear stages.
