import { auth } from "../../../firebase";

const BACKEND_URL = (process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000").replace(/\/$/, "");

async function request(path, method = "GET", body) {
  const currentUser = auth.currentUser;
  if (!currentUser) throw new Error("Sign in before updating your profile.");
  const token = await currentUser.getIdToken();
  const response = await fetch(`${BACKEND_URL}${path}`, {
    method,
    headers: { Authorization: `Bearer ${token}`, ...(body ? { "Content-Type": "application/json" } : {}) },
    ...(body ? { body: JSON.stringify(body) } : {}),
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || `Backend request failed (${response.status}).`);
  return data;
}

export async function ensureUserProfile(user) {
  if (!user) return null;
  const result = await request("/api/auth/verify", "POST", { token: await user.getIdToken() });
  return result.user;
}

export async function createUserProfile() {
  const result = await request("/api/auth/sync-user", "POST", {});
  return result.user;
}

export async function updateUserProfile(_uid, profileData) {
  const result = await request("/api/auth/profile", "PUT", {
    displayName: profileData.displayName,
    full_name: profileData.full_name || profileData.displayName,
    language: profileData.language,
    timezone: profileData.timezone,
    role: profileData.role,
  });
  return result.user;
}
