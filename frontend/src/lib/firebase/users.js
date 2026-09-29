import { db, auth } from "../../../firebase";
import { doc, getDoc, setDoc, updateDoc, serverTimestamp } from "firebase/firestore";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:5000";

/**
 * Verifies token with FastAPI backend (which verifies Firebase ID token)
 * and retrieves/creates user profile in Supabase profiles table.
 */
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
    console.warn("FastAPI backend verification unavailable, using client Firestore fallback:", err.message);
  }

  // Fallback directly to client Firestore if backend endpoint is unreachable
  try {
    const userRef = doc(db, "users", user.uid);
    const snap = await getDoc(userRef);

    if (!snap.exists()) {
      const newUser = {
        uid: user.uid,
        firebase_uid: user.uid,
        email: user.email || "",
        displayName: user.displayName || (user.email ? user.email.split("@")[0] : "User"),
        full_name: user.displayName || (user.email ? user.email.split("@")[0] : "User"),
        photoURL: user.photoURL || "",
        role: "user",
        createdAt: new Date().toISOString(),
      };
      await setDoc(userRef, newUser);
      return newUser;
    }

    return snap.data();
  } catch (clientErr) {
    console.error("User profile sync error:", clientErr);
    return {
      uid: user.uid,
      firebase_uid: user.uid,
      email: user.email,
      displayName: user.displayName || "User",
      full_name: user.displayName || "User",
    };
  }
}

/**
 * Creates or syncs user profile in Supabase via FastAPI backend.
 */
export async function createUserProfile(uid, profileData) {
  try {
    if (auth.currentUser) {
      const idToken = await auth.currentUser.getIdToken();
      const res = await fetch(`${BACKEND_URL}/api/auth/sync-user`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${idToken}`,
        },
        body: JSON.stringify({
          uid,
          email: profileData.email,
          displayName: profileData.displayName,
          full_name: profileData.full_name || profileData.displayName,
          role: profileData.role || "user",
        }),
      });

      if (res.ok) {
        const data = await res.json();
        if (data.success && data.user) {
          return data.user;
        }
      }
    }
  } catch (backendErr) {
    console.warn("Backend sync failed, falling back to Firestore client:", backendErr);
  }

  // Fallback to Firestore client
  try {
    const userRef = doc(db, "users", uid);
    const dataToSave = {
      uid,
      ...profileData,
      createdAt: serverTimestamp(),
      updatedAt: serverTimestamp(),
    };
    await setDoc(userRef, dataToSave, { merge: true });
    return dataToSave;
  } catch (err) {
    console.error("Error creating user profile:", err);
    return { uid, ...profileData };
  }
}

/**
 * Updates an existing user profile in Supabase via FastAPI backend.
 */
export async function updateUserProfile(uid, profileData) {
  try {
    if (auth.currentUser) {
      const idToken = await auth.currentUser.getIdToken();
      const res = await fetch(`${BACKEND_URL}/api/auth/profile`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${idToken}`,
        },
        body: JSON.stringify({
          displayName: profileData.displayName,
          full_name: profileData.full_name || profileData.displayName,
          role: profileData.role,
          language: profileData.language,
          timezone: profileData.timezone,
        }),
      });

      if (res.ok) {
        const data = await res.json();
        if (data.success) {
          return data.user;
        }
      }
    }
  } catch (backendErr) {
    console.warn("Backend update failed, falling back to Firestore client:", backendErr);
  }

  // Fallback to Firestore client
  try {
    const userRef = doc(db, "users", uid);
    await updateDoc(userRef, {
      ...profileData,
      updatedAt: serverTimestamp(),
    });
    return true;
  } catch (err) {
    console.error("Error updating user profile:", err);
    return createUserProfile(uid, profileData);
  }
}

