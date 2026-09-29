# GitLab AI Content & Documentation Engine 🚀

A multi-agent AI-driven platform built for automated creation, refinement, review, and management of technical documentation, GitLab release notes, API references, user guides, and tech blogs.

---

## 🌟 Key Features

* **🔐 Authentication & User Management**:
  * Seamless sign-in via **Google OAuth** or **Email & Password**.
  * Powered by **Firebase Auth** on the frontend and verified server-side with **Firebase Admin SDK** (`serviceAccountKey.json`).
  * User profile persistence and role management powered by **Cloud Firestore**.
  * Dynamic route guarding (`AuthGuard`) protecting application pages.

* **📊 Dashboard & Metrics**:
  * Live overview of content jobs, drafts created, editorial reviews, and published documents.
  * Real-time content pipeline visualization (Intake ➔ Context ➔ Draft ➔ Refine ➔ Review ➔ Publish).

* **📝 AI Content Generator (`/create-content`)**:
  * Generate release notes, API documentation, and blogs directly from GitLab Merge Requests (MRs) or raw notes.
  * Multi-agent workflows for tone optimization, formatting, and technical accuracy.

* **📂 Job & Workflow Management (`/my-jobs`, `/review`)**:
  * Track active generation tasks, draft status, and editorial review steps.
  * In-line content review and refinement.

* **📚 Knowledge Base & Templates (`/knowledge-base`, `/templates`)**:
  * Pre-configured templates for GitLab release announcements, API references, self-hosted guides, and onboarding docs.
  * Team repository storing context documents and documentation guidelines.

* **⚙️ User Preferences & Settings (`/settings`)**:
  * Profile management, role selection (Developer, Product Manager, Designer), regional preferences, and AI engine settings.

---

## 🏗️ Architecture & Technology Stack

### Frontend
* **Framework**: [Next.js 16](https://nextjs.org/) (App Router) & [React 19](https://react.dev/)
* **Styling**: [Tailwind CSS v4](https://tailwindcss.com/)
* **Icons**: [React Icons](https://react-icons.github.io/react-icons/) (`react-icons/fi`, `react-icons/fa`)
* **Auth & Data**: Firebase Client SDK v12 (Auth & Firestore)

### Backend
* **Runtime**: [Node.js](https://nodejs.org/) (ES Modules)
* **Framework**: [Express 5](https://expressjs.com/)
* **Security & Admin**: Firebase Admin SDK v14 (`firebase-admin`)
* **Database**: Google Cloud Firestore & Mongoose / MongoDB

---

## 📁 Repository Structure

```text
gitlab-ai-content-engine/
├── backend/
│   ├── index.js                     # Express API server entry point
│   ├── middleware/
│   │   └── authMiddleware.js        # Firebase Admin auth verification middleware
│   ├── routes/
│   │   └── authRoutes.js            # Authentication API endpoints (/verify, /sync-user, /me)
│   ├── serviceAccountKey.json       # Firebase Admin service account key
│   └── package.json                 # Backend dependencies & scripts
│
├── frontend/
│   ├── firebase.js                  # Firebase Client SDK initialization
│   ├── src/
│   │   ├── app/                     # Next.js App Router routes & pages
│   │   │   ├── login/               # Sign-in page
│   │   │   ├── signup/              # Account creation page
│   │   │   ├── dashboard/           # Main workspace dashboard
│   │   │   ├── create-content/      # AI Content generator interface
│   │   │   ├── my-jobs/             # Content job management
│   │   │   ├── review/              # Editorial review workflow
│   │   │   ├── knowledge-base/      # Team knowledge base
│   │   │   ├── templates/           # Document templates
│   │   │   ├── analytics/           # Content metrics & analytics
│   │   │   └── settings/            # User settings & AI config
│   │   ├── components/
│   │   │   └── layout/              # AppHeader, SidebarNav, AppLayout, AuthGuard
│   │   ├── hooks/
│   │   │   └── useAuth.js           # AuthContext & useAuth custom hook
│   │   └── lib/
│   │       └── firebase/            # Firestore user profile utilities
│   └── package.json                 # Frontend dependencies & scripts
│
└── README.md                        # Project documentation
```

---

## ⚡ Getting Started

### Prerequisites
* **Node.js**: `v18+` or `v20+` installed
* **npm** or **yarn** / **pnpm**
* **Firebase Account**: Cloud Firestore & Authentication enabled

---

### 1. Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install backend dependencies:
   ```bash
   npm install
   ```

3. Configure Firebase Admin Service Account Key:
   Ensure `serviceAccountKey.json` is present in `backend/serviceAccountKey.json`.

4. Start the backend development server:
   ```bash
   npm run dev
   ```
   The backend API runs at `http://localhost:5000`.

---

### 2. Frontend Setup

1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install frontend dependencies:
   ```bash
   npm install
   ```

3. Environment Variables (Optional):
   Create a `.env.local` file inside `frontend/` if overriding default Firebase settings:
   ```env
   NEXT_PUBLIC_FIREBASE_API_KEY=your_api_key
   NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=generative-ai-3bba7.firebaseapp.com
   NEXT_PUBLIC_FIREBASE_PROJECT_ID=generative-ai-3bba7
   NEXT_PUBLIC_BACKEND_URL=http://localhost:5000
   ```

4. Start the Next.js development server:
   ```bash
   npm run dev
   ```
   Open `http://localhost:3000` in your browser.

---

## 🚀 Navigation & Application Pages

Once authenticated via Google or Email/Password, users access the following sections:

| Route | Page Name | Description |
| :--- | :--- | :--- |
| `/dashboard` | **Dashboard** | Overview of jobs, pipeline statuses, recent activity, and quick actions. |
| `/create-content` | **Create Content** | AI-assisted documentation generator from MRs, code commits, and prompt templates. |
| `/my-jobs` | **My Jobs** | List of all ongoing and completed content generation tasks. |
| `/review` | **Review** | Editorial workspace for content refinement and team sign-offs. |
| `/knowledge-base` | **Knowledge Base** | Repository for team context, documentation guidelines, and reference assets. |
| `/templates` | **Templates** | Library of standardized documentation formats and prompts. |
| `/analytics` | **Analytics** | Metrics on content volume, generation speed, and review cycles. |
| `/settings` | **Settings** | Manage account details, user role, localization preferences, and AI configs. |

---

## 🔒 Security & Middleware

* **Token Verification**: Every authenticated request passes a Firebase ID Token in the `Authorization: Bearer <token>` header to the backend `/api/auth/verify` endpoint.
* **Server-side Validation**: The backend uses `firebaseAdmin.auth().verifyIdToken()` to validate user credentials against the project's service account.
* **Firestore Access**: User documents are safely synced in Firestore using backend service account privileges and client security rules.

---

## 📄 License

This project is maintained for **GitLab AI Content Engine** development. All rights reserved.
