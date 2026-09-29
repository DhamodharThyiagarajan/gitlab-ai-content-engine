"use client";

import { useEffect, useState } from "react";
import AppLayout from "@/components/layout/AppLayout";
import { useAuth } from "@/hooks/useAuth";
import { updateUserProfile } from "@/lib/firebase/users";

const navTabs = ["Profile", "AI Configuration", "Notifications", "Integrations", "Security"];

export default function SettingsPage() {
  const { user, userProfile, refreshProfile } = useAuth();
  const [displayName, setDisplayName] = useState("");
  const [role, setRole] = useState("Developer");
  const [language, setLanguage] = useState("English");
  const [timezone, setTimezone] = useState("(GMT+5:30) India Standard Time");
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    if (!userProfile) {
      return;
    }

    setDisplayName(userProfile.displayName || "");
    setRole(userProfile.role || "Developer");
    setLanguage(userProfile.language || "English");
    setTimezone(userProfile.timezone || "(GMT+5:30) India Standard Time");
  }, [userProfile]);

  async function handleSave() {
    if (!user) {
      return;
    }

    setSaving(true);
    setMessage("");
    setError("");

    try {
      await updateUserProfile(user.uid, {
        displayName,
        role,
        language,
        timezone,
      });
      await refreshProfile();
      setMessage("Settings saved successfully.");
    } catch (err) {
      setError(err?.message || "Failed to save settings.");
    } finally {
      setSaving(false);
    }
  }

  const email = userProfile?.email || user?.email || "";
  const initial = (displayName || email || "U").charAt(0).toUpperCase();

  return (
    <AppLayout initialSelectedNav="Settings">
      <div className="flex h-full flex-1 flex-col px-3 py-4 sm:px-4 md:px-5 lg:px-6 xl:px-8">
        <div className="flex h-full flex-1 flex-col rounded-[26px] border border-[#f0ddd2] bg-[#fffaf7] p-3 shadow-[0_8px_24px_rgba(57,44,38,0.04)] sm:p-4 md:p-5 lg:p-6">
          <div className="flex items-center justify-between gap-3 pb-4">
            <div>
              <h1 className="text-[2.4rem] font-semibold tracking-[-0.06em] text-[#1d2430]">Settings</h1>
              <p className="mt-1 text-[1.05rem] text-[#6d757f]">
                Manage your account, preferences and application settings.
              </p>
            </div>
          </div>

          <div className="mt-5 flex flex-wrap gap-6 border-b border-[#efe2d6] pb-3 text-[0.95rem] font-medium text-[#53606f]">
            {navTabs.map((tab, index) => (
              <button
                key={tab}
                type="button"
                className={`relative pb-2 transition ${
                  index === 0
                    ? "text-[#1f2530] after:absolute after:bottom-[-11px] after:left-0 after:h-[3px] after:w-full after:rounded-full after:bg-[#f56d2a]"
                    : "hover:text-[#1b2028]"
                }`}
              >
                {tab}
              </button>
            ))}
          </div>

          <div className="mt-6 grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
            <section className="rounded-[22px] border border-[#f1e5dc] bg-[#fffdfb] p-4 sm:p-5">
              <div className="flex items-center gap-5">
                <div className="flex items-center justify-center overflow-hidden rounded-full border border-[#e8dccc] bg-[#e9ebf2] text-[1.3rem] font-semibold text-[#3f4a5b]">
                  <div className="flex h-20 w-20 items-center justify-center bg-[radial-gradient(circle_at_30%_30%,_#f0f4ff_0%,_#d8dfe9_25%,_#b8c1cf_100%)] text-[#1d2430]">
                    {initial}
                  </div>
                </div>

                <div className="flex-1">
                  <div className="flex items-center gap-3">
                    <div className="text-[1.1rem] font-semibold text-[#1d2430]">{displayName || "User"}</div>
                  </div>
                  <div className="mt-3 text-[0.96rem] text-[#677181]">{email}</div>
                </div>
              </div>

              <div className="mt-6 grid gap-4 md:grid-cols-2">
                <label className="block text-sm font-medium text-[#3f4a5b]">
                  <span className="mb-2 block">Full Name</span>
                  <input
                    value={displayName}
                    onChange={(e) => setDisplayName(e.target.value)}
                    className="h-12 w-full rounded-xl border border-[#e8d9cd] bg-[#f9f6f3] px-3 text-base text-[#20262e] outline-none focus:border-[#f56d2a]"
                  />
                </label>

                <label className="block text-sm font-medium text-[#3f4a5b]">
                  <span className="mb-2 block">Email Address</span>
                  <input
                    value={email}
                    readOnly
                    className="h-12 w-full rounded-xl border border-[#e8d9cd] bg-[#f9f6f3] px-3 text-base text-[#20262e] outline-none"
                  />
                </label>

                <label className="block text-sm font-medium text-[#3f4a5b] md:col-span-2">
                  <span className="mb-2 block">Role</span>
                  <select
                    value={role}
                    onChange={(e) => setRole(e.target.value)}
                    className="h-12 w-full rounded-xl border border-[#e8d9cd] bg-[#f9f6f3] px-3 text-base text-[#20262e] outline-none focus:border-[#f56d2a]"
                  >
                    <option>Developer</option>
                    <option>Product Manager</option>
                    <option>Designer</option>
                  </select>
                </label>
              </div>
            </section>

            <section className="rounded-[22px] border border-[#f1e5dc] bg-[#fffdfb] p-4 sm:p-5">
              <h2 className="text-[1.8rem] font-semibold tracking-[-0.05em] text-[#1d2430]">Preferences</h2>

              <div className="mt-6 space-y-5">
                <label className="block text-sm font-medium text-[#3f4a5b]">
                  <span className="mb-2 block">Language</span>
                  <select
                    value={language}
                    onChange={(e) => setLanguage(e.target.value)}
                    className="h-12 w-full rounded-xl border border-[#e8d9cd] bg-[#f9f6f3] px-3 text-base text-[#20262e] outline-none focus:border-[#f56d2a]"
                  >
                    <option>English</option>
                    <option>Spanish</option>
                    <option>French</option>
                  </select>
                </label>

                <label className="block text-sm font-medium text-[#3f4a5b]">
                  <span className="mb-2 block">Timezone</span>
                  <select
                    value={timezone}
                    onChange={(e) => setTimezone(e.target.value)}
                    className="h-12 w-full rounded-xl border border-[#e8d9cd] bg-[#f9f6f3] px-3 text-base text-[#20262e] outline-none focus:border-[#f56d2a]"
                  >
                    <option>(GMT+5:30) India Standard Time</option>
                    <option>(GMT+0:00) UTC</option>
                    <option>(GMT-8:00) Pacific Time</option>
                  </select>
                </label>

                {message && (
                  <div className="rounded-md bg-green-50 px-4 py-2 text-sm text-green-700">{message}</div>
                )}

                {error && (
                  <div className="rounded-md bg-red-50 px-4 py-2 text-sm text-red-700">{error}</div>
                )}

                <button
                  type="button"
                  onClick={handleSave}
                  disabled={saving}
                  className="mt-2 w-full rounded-xl bg-[#f56d2a] px-4 py-3 text-base font-semibold text-white shadow-[0_10px_18px_rgba(245,109,42,0.24)] transition hover:bg-[#e55f1c] disabled:opacity-60"
                >
                  {saving ? "Saving..." : "Save Changes"}
                </button>
              </div>
            </section>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
