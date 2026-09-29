"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { onAuthStateChanged, signOut as firebaseSignOut } from "firebase/auth";
import { auth } from "../../firebase";
import { ensureUserProfile } from "@/lib/firebase/users";

const AuthContext = createContext({
  user: null,
  userProfile: null,
  idToken: null,
  loading: true,
  logout: async () => {},
  refreshProfile: async () => {},
});

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [userProfile, setUserProfile] = useState(null);
  const [idToken, setIdToken] = useState(null);
  const [loading, setLoading] = useState(true);

  const syncUserWithBackend = async (currentUser) => {
    if (!currentUser) {
      setUser(null);
      setUserProfile(null);
      setIdToken(null);
      setLoading(false);
      return;
    }

    try {
      const token = await currentUser.getIdToken();
      setIdToken(token);
      setUser(currentUser);

      const profile = await ensureUserProfile(currentUser);
      setUserProfile(profile || {
        uid: currentUser.uid,
        email: currentUser.email,
        displayName: currentUser.displayName || currentUser.email?.split("@")[0] || "User",
      });
    } catch (error) {
      console.error("Error syncing auth state with backend:", error);
      setUser(currentUser);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      syncUserWithBackend(currentUser);
    });

    return () => unsubscribe();
  }, []);

    const logout = async () => {
      setLoading(true);
      try {
        await firebaseSignOut(auth);
        setUser(null);
        setUserProfile(null);
        setIdToken(null);
      } catch (error) {
        console.error("Logout error:", error);
      } finally {
        setLoading(false);
      }
    };

  const refreshProfile = async () => {
    if (auth.currentUser) {
      await syncUserWithBackend(auth.currentUser);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        userProfile,
        idToken,
        loading,
        logout,
        refreshProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}