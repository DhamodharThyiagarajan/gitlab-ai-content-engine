# FastAPI + Firebase Auth + Supabase (SQLAlchemy ORM) Backend

This backend is built with **FastAPI (Python)** using **SQLAlchemy ORM** to manage user profiles in **Supabase / PostgreSQL**, integrated with **Firebase Authentication** for identity verification.

---

## 🏗️ Architecture Flow

```
Firebase Auth (Client: Email/Password or Google Sign-In)
       │
       │ User signs up / logs in
       ▼
Firebase UID & ID Token (Bearer token)
       │
       │ POST /api/auth/verify (Authorization: Bearer <idToken>)
       ▼
FastAPI Backend (Python)
       │
       │ Verify Token with Firebase Admin SDK
       │ Create / Find User Profile using SQLAlchemy ORM
       ▼
Supabase Database (PostgreSQL via SQLAlchemy ORM)
┌─────────────────────────────────────────┐
│ public.profiles                         │
│ ─────────────────────────────────────── │
│ id           UUID / VARCHAR(36) PK      │
│ firebase_uid VARCHAR(255) UNIQUE        │
│ email        VARCHAR(255)               │
│ full_name    VARCHAR(255)               │
│ role         VARCHAR(50) DEFAULT 'user' │
│ created_at   TIMESTAMPTZ                │
│ updated_at   TIMESTAMPTZ                │
└─────────────────────────────────────────┘
```

---

## 🛠️ SQLAlchemy ORM Model (`Profile`)

Defined in `models.py`:
- `id`: Primary key UUID string
- `firebase_uid`: Unique string indexed for fast user profile lookups
- `email`: User email address
- `full_name`: User's full name
- `role`: Role string (default: `"user"`)
- `created_at`: Timestamp with time zone
- `updated_at`: Timestamp with time zone

---

## 🚀 Quick Start Instructions

### 1. Configure Environment (`backend/.env`)
Set your Supabase PostgreSQL connection string in `backend/.env`:
```env
PORT=5000
FIREBASE_SERVICE_ACCOUNT_PATH=serviceAccountKey.json

# Supabase PostgreSQL Connection String
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
```
*(If no DATABASE_URL is supplied, it automatically defaults to local SQLite database `sqlite:///./app.db` for instant development).*

### 2. Run FastAPI Backend
```bash
cd backend
.venv\Scripts\activate
python -m uvicorn main:app --reload --port 5000
```
*SQLAlchemy automatically creates the `profiles` table on server startup if it does not already exist.*
