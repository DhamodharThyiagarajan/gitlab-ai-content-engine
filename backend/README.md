# GitLab AI Content Engine Backend

This backend is a FastAPI application that authenticates users with Firebase and stores synced user profile data using SQLAlchemy ORM. It supports PostgreSQL/Supabase when configured and falls back to SQLite for local development.

## Architecture

```text
Firebase Auth
    │
    ├── User signs in with Email/Password or Google
    │
    ▼
FastAPI backend
    │
    ├── Verifies Firebase ID token
    ├── Creates or updates profile in SQLAlchemy database
    └── Exposes auth endpoints for frontend use
    │
    ▼
Database (Supabase Postgres or SQLite fallback)
```

## Stack

- Python
- FastAPI
- SQLAlchemy
- Firebase Admin SDK
- PostgreSQL / Supabase
- SQLite fallback for local dev

## Project Structure

```text
backend/
├── main.py
├── config.py
├── models.py
├── requirements.txt
├── serviceAccountKey.json
├── database/
│   ├── __init__.py
│   └── client.py
├── auth/
│   ├── __init__.py
│   ├── dependencies.py
│   └── firebase.py
├── routers/
│   └── auth_routes.py
└── README.md
```

## Environment Variables

Create a `.env` file inside the `backend` folder:

```env
PORT=5000
DATABASE_URL=postgresql://postgres:your_password@db.your-project.supabase.co:5432/postgres
FIREBASE_SERVICE_ACCOUNT_PATH=serviceAccountKey.json
ENABLE_DEV_USER_CREATION=false
```

Notes:
- If `DATABASE_URL` is not set, the app uses SQLite automatically: `sqlite:///./app.db`
- The Firebase service account JSON file is expected in `backend/serviceAccountKey.json`

## Database Model

The backend stores users in a `profiles` table:

- `id` - UUID primary key
- `firebase_uid` - unique Firebase user ID
- `email` - user email
- `full_name` - user display name
- `role` - role string, default `user`
- `created_at` - timestamp
- `updated_at` - timestamp

This is defined in [models.py](models.py).

## Startup

From the project root:

```bash
cd backend
.venv\Scripts\activate
python -m uvicorn main:app --reload --port 5000
```

Or from PowerShell if using a virtual environment:

```powershell
cd D:\projects\gitlab-ai-content-engine\backend
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
. .\.venv\Scripts\Activate.ps1
python -m uvicorn main:app --reload --port 5000
```

The API will be available at:

```text
http://localhost:5000
```

## Auth Endpoints

These are exposed via the router in [routers/auth_routes.py](routers/auth_routes.py):

### POST `/api/auth/verify`
Verifies a Firebase ID token and creates or syncs the user profile.

Example headers:

```http
Authorization: Bearer <firebase_id_token>
```

### POST `/api/auth/sync-user`
Syncs profile details for the authenticated user.

### GET `/api/auth/me`
Returns the current authenticated user's profile.

### POST `/api/auth/profile` or `PUT /api/auth/profile`
Updates profile information.

## Health Check

```bash
GET /health
```

Returns a basic API status response.

## Notes

- This backend expects the frontend to send a Firebase bearer token for authenticated requests.
- Firebase token verification is handled server-side using the Admin SDK.
- The app initializes database tables automatically during startup.
