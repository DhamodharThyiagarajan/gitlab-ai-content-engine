# Firebase Authentication & Firestore Architecture Guide 🔐🔥

This document provides a deep-dive walkthrough into how **Firebase Authentication** and **Cloud Firestore** are configured and integrated across the **Next.js Frontend** and **Express Backend** in the **GitLab AI Content Engine**.

---

## 📑 Table of Contents

1. [Architecture Overview](#-architecture-overview)
2. [End-to-End Authentication Flow](#-end-to-end-authentication-flow)
3. [Firebase Console Configuration Guide](#-firebase-console-configuration-guide)
   * [Frontend Configuration (.env.local)](#1-frontend-configuration-envlocal)
   * [Backend Configuration (serviceAccountKey.json)](#2-backend-configuration-serviceaccountkeyjson)
4. [Code Implementation Walkthrough](#-code-implementation-walkthrough)
   * [1. Frontend Firebase Initialization (`frontend/firebase.js`)](#1-frontend-firebase-initialization-frontendfirebasejs)
   * [2. Client Profile & Verification Service (`frontend/src/lib/firebase/users.js`)](#2-client-profile--verification-service-frontendsrclibfirebaseusersjs)
   * [3. React Auth Context & Hook (`frontend/src/hooks/useAuth.js`)](#3-react-auth-context--hook-frontendsrchooksuseauthjs)
   * [4. Protected Route Guard (`frontend/src/components/layout/AuthGuard.js`)](#4-protected-route-guard-frontendsrccomponentslayoutauthguardjs)
   * [5. Backend Admin SDK Middleware (`backend/middleware/authMiddleware.js`)](#5-backend-admin-sdk-middleware-backendmiddlewareauthmiddlewarejs)
   * [6. Backend Authentication API Routes (`backend/routes/authRoutes.js`)](#6-backend-authentication-api-routes-backendroutesauthroutesjs)
5. [Cloud Firestore Data Model](#-cloud-firestore-data-model)
6. [Troubleshooting Common Issues](#-troubleshooting-common-issues)

---

## 🏗️ Architecture Overview

The application utilizes a **hybrid security model**:
* **Frontend (Client-side)**: Firebase Web SDK (v12) manages authentication UI, OAuth popups (Google), Email/Password sessions, and initial token retrieval.
* **Backend (Server-side)**: Express.js with Firebase Admin SDK (v14) cryptographically validates Firebase ID Tokens using Google Service Account credentials (`serviceAccountKey.json`) and manages Firestore user records directly with admin privileges.

```text
 ┌───────────────────────────┐                ┌───────────────────────────┐
 │   Next.js Frontend        │                │    Express Backend        │
 │   (Firebase Client SDK)   │                │   (Firebase Admin SDK)    │
 └─────────────┬─────────────┘                └─────────────┬─────────────┘
               │                                            │
               │  1. Login with Google / Email              │
               ├───────────────────────────────────────────►│
               │                                            │
               │  2. Obtains Firebase ID Token              │
               │                                            │
               │  3. POST /api/auth/verify (Bearer Token)   │
               ├───────────────────────────────────────────►│
               │                                            │  4. verifyIdToken(token)
               │                                            ├───────────────────────┐
               │                                            │                       │
               │                                            │  5. Fetch/Create Doc  │
               │                                            │     in Firestore      │
               │                                            │◄──────────────────────┘
               │  6. Returns Verified User Object           │
               │◄───────────────────────────────────────────┤
               │                                            │
               │  7. Navigates to Protected Pages           │
               │     (/dashboard, /create-content, etc.)    │
```

---

## 🔄 End-to-End Authentication Flow

1. **User Action**: User enters credentials or clicks **Continue with Google** on `/login` or `/signup`.
2. **Client Sign-In**: Firebase Client SDK handles authentication:
   * Google: `signInWithPopup(auth, googleProvider)`
   * Email/Password: `signInWithEmailAndPassword(auth, email, password)` / `createUserWithEmailAndPassword(auth, email, password)`
3. **Token Extraction**: The client retrieves a signed JWT ID Token: `const token = await user.getIdToken()`.
4. **Backend Verification**: Client calls `ensureUserProfile(user)` which sends a `POST` request to `http://localhost:5000/api/auth/verify` with header `Authorization: Bearer <idToken>`.
5. **Server Validation**: The Express backend uses `auth.verifyIdToken(token)` via `serviceAccountKey.json` to verify signature, expiration, and issuer.
6. **Firestore User Sync**: If verified, backend checks Firestore collection `users/{uid}`:
   * If document exists: Updates `lastLoginAt`.
   * If new user: Creates user document with default role `"user"`.
7. **Session Persistence**: React `AuthContext` stores user & profile data. `AuthGuard` allows navigation to all protected routes (`/dashboard`, `/settings`, etc.).

---

## ⚙️ Firebase Console Configuration Guide

### 1. Frontend Configuration (`.env.local`)

1. Go to [Firebase Console](https://console.firebase.google.com/) ➔ Select Project **`generative-ai-3bba7`**.
2. Click ⚙️ **Project Settings** ➔ **General** ➔ Scroll to **Your apps**.
3. Copy your Web App configuration keys into `frontend/.env.local`:

```env
NEXT_PUBLIC_FIREBASE_API_KEY=AIzaSyDPy5uiC76CSJ2sLY8KJBwQcIugnvDwfOg
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=generative-ai-3bba7.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=generative-ai-3bba7
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=generative-ai-3bba7.firebasestorage.app
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=856283466098
NEXT_PUBLIC_FIREBASE_APP_ID=1:856283466098:web:196b1a76e89c9883c1f5eb
NEXT_PUBLIC_BACKEND_URL=http://localhost:5000
```

---

### 2. Backend Configuration (`serviceAccountKey.json`)

1. In Firebase Console, navigate to ⚙️ **Project Settings** ➔ **Service accounts** tab.
2. Click **Generate new private key** (downloads a `.json` key file).
3. Place this JSON file at `backend/serviceAccountKey.json`.

---

## 💻 Code Implementation Walkthrough

### 1. Frontend Firebase Initialization (`frontend/firebase.js`)

Initializes Firebase Web App, Auth, Google OAuth Provider, and Firestore instance.

```javascript
import { initializeApp, getApps, getApp } from "firebase/app";
import { getAuth, GoogleAuthProvider } from "firebase/auth";
import { getFirestore } from "firebase/firestore";

const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY || "AIzaSyDPy5uiC76CSJ2sLY8KJBwQcIugnvDwfOg",
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN || "generative-ai-3bba7.firebaseapp.com",
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID || "generative-ai-3bba7",
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET || "generative-ai-3bba7.firebasestorage.app",
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID || "856283466098",
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID || "1:856283466098:web:196b1a76e89c9883c1f5eb",
};

const app = getApps().length > 0 ? getApp() : initializeApp(firebaseConfig);

export const auth = getAuth(app);
export const googleProvider = new GoogleAuthProvider();
googleProvider.setCustomParameters({ prompt: "select_account" });
export const db = getFirestore(app);

export default app;
```

---

### 2. Client Profile & Verification Service (`frontend/src/lib/firebase/users.js`)

Sends token to backend for server-side validation and profile sync:

```javascript
import { db } from "../../../firebase";
import { doc, getDoc, setDoc, updateDoc, serverTimestamp } from "firebase/firestore";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:5000";

export async function ensureUserProfile(user) {
  if (!user) return null;

  try {
    const idToken = await user.getIdToken(true);

    const res = await fetch(`${BACKEND_URL}/api/auth/verify`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${idToken}`,
      },
      body: JSON.stringify({ token: idToken }),
    });

    if (res.ok) {
      const data = await res.json();
      if (data.success && data.user) {
        return data.user;
      }
    }
  } catch (err) {
    console.warn("Backend verification fallback to client Firestore:", err.message);
  }

  // Client Firestore fallback
  const userRef = doc(db, "users", user.uid);
  const snap = await getDoc(userRef);
  if (!snap.exists()) {
    const newUser = {
      uid: user.uid,
      email: user.email || "",
      displayName: user.displayName || "User",
      role: "user",
      createdAt: new Date().toISOString(),
    };
    await setDoc(userRef, newUser);
    return newUser;
  }
  return snap.data();
}
```

---

### 3. React Auth Context & Hook (`frontend/src/hooks/useAuth.js`)

Provides global authentication state across all React components.

```javascript
"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { onAuthStateChanged, signOut as firebaseSignOut } from "firebase/auth";
import { auth } from "../../firebase";
import { ensureUserProfile } from "@/lib/firebase/users";

const AuthContext = createContext({ user: null, userProfile: null, loading: true, logout: async () => {} });

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [userProfile, setUserProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (currentUser) => {
      if (currentUser) {
        setUser(currentUser);
        const profile = await ensureUserProfile(currentUser);
        setUserProfile(profile);
      } else {
        setUser(null);
        setUserProfile(null);
      }
      setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  const logout = async () => {
    await firebaseSignOut(auth);
    setUser(null);
    setUserProfile(null);
  };

  return (
    <AuthContext.Provider value={{ user, userProfile, loading, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
```

---

### 4. Protected Route Guard (`frontend/src/components/layout/AuthGuard.js`)

Protects application pages (`/dashboard`, `/create-content`, `/settings`, etc.) from unauthenticated access.

```javascript
"use client";

import { useAuth } from "@/hooks/useAuth";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function AuthGuard({ children }) {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) {
      router.replace("/login");
    }
  }, [loading, user, router]);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#f7f1eb]">
        <div className="animate-spin h-8 w-8 rounded-full border-4 border-[#f56d2a] border-t-transparent" />
      </div>
    );
  }

  return user ? <>{children}</> : null;
}
```

---

### 5. Backend Admin SDK Middleware (`backend/middleware/authMiddleware.js`)

Initializes `firebase-admin` using modular imports (`firebase-admin/app`, `firebase-admin/auth`, `firebase-admin/firestore`) and verifies Bearer tokens.

```javascript
import { initializeApp, getApps, cert } from "firebase-admin/app";
import { getAuth } from "firebase-admin/auth";
import { getFirestore } from "firebase-admin/firestore";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const serviceAccountPath = path.resolve(__dirname, "../serviceAccountKey.json");
const serviceAccount = JSON.parse(fs.readFileSync(serviceAccountPath, "utf8"));

const app = getApps().length === 0
  ? initializeApp({ credential: cert(serviceAccount) })
  : getApps()[0];

export const auth = getAuth(app);
export const db = getFirestore(app);

export const protect = async (req, res, next) => {
  const authHeader = req.headers.authorization;

  if (!authHeader || !authHeader.startsWith("Bearer ")) {
    return res.status(401).json({ message: "Unauthorized" });
  }

  const token = authHeader.split(" ")[1];

  try {
    const decoded = await auth.verifyIdToken(token);
    req.user = decoded;
    next();
  } catch (error) {
    return res.status(401).json({ message: "Unauthorized", error: error.message });
  }
};
```

---

### 6. Backend Authentication API Routes (`backend/routes/authRoutes.js`)

```javascript
import express from "express";
import { auth, db, protect } from "../middleware/authMiddleware.js";

const router = express.Router();

router.post("/verify", async (req, res) => {
  try {
    const token = req.body.token || req.headers.authorization?.split(" ")[1];
    const decodedToken = await auth.verifyIdToken(token);
    const { uid, email, name, picture } = decodedToken;

    const userRef = db.collection("users").doc(uid);
    const userDoc = await userRef.get();

    let userData;
    if (!userDoc.exists) {
      userData = {
        uid,
        email: email || "",
        displayName: name || email?.split("@")[0] || "User",
        photoURL: picture || "",
        role: "user",
        createdAt: new Date().toISOString(),
        lastLoginAt: new Date().toISOString(),
      };
      await userRef.set(userData);
    } else {
      userData = userDoc.data();
      await userRef.update({ lastLoginAt: new Date().toISOString() });
    }

    return res.json({ success: true, user: userData });
  } catch (error) {
    return res.status(401).json({ success: false, message: error.message });
  }
});

export default router;
```

---

## 🗄️ Cloud Firestore Data Model

### `users` Collection Document Schema (`users/{uid}`)

```json
{
  "uid": "L8kJ2sLY8KJBwQcIugnvDwfOg123",
  "email": "user@gitlab-engine.com",
  "displayName": "Dhamo Developer",
  "photoURL": "https://lh3.googleusercontent.com/a/...",
  "role": "Developer",
  "language": "English",
  "timezone": "(GMT+5:30) India Standard Time",
  "createdAt": "2026-09-25T11:00:00.000Z",
  "lastLoginAt": "2026-09-25T11:30:00.000Z"
}
```

---

## 🛠️ Troubleshooting Common Issues

| Error Message | Cause | Solution |
| :--- | :--- | :--- |
| `auth/api-key-not-valid` | Invalid or missing `NEXT_PUBLIC_FIREBASE_API_KEY` | Ensure `frontend/.env.local` contains the valid API key from Firebase Console. |
| `TypeError: Cannot read properties of undefined (reading 'length')` | Using legacy default import `import admin from "firebase-admin"` in v14+ | Use modular SDK imports: `import { initializeApp } from "firebase-admin/app"`. |
| `auth/popup-closed-by-user` | User closed Google sign-in window before authorizing | User needs to re-attempt sign in. |
| `Unauthorized / 401` on backend | Expired or invalid Bearer ID Token | Frontend `getIdToken(true)` forces token refresh before request. |
