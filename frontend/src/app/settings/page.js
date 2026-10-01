"use client";

import { useEffect, useState } from "react";
import AppLayout from "@/components/layout/AppLayout";
import { useAuth } from "@/hooks/useAuth";
import { updateUserProfile } from "@/lib/firebase/users";

const navTabs = ["Profile", "AI Configuration", "Notifications", "Integrations", "Security"];
const roleOptions = ["writer", "reviewer", "approver", "admin"];
const permissionMatrix = {
  writer: { refine: true, requestRevision: false, approve: false, publish: false },
  reviewer: { refine: true, requestRevision: true, approve: true, publish: false },
  approver: { refine: true, requestRevision: true, approve: true, publish: true },
  admin: { refine: true, requestRevision: true, approve: true, publish: true },
};

export default function SettingsPage() {
  const { user, userProfile, refreshProfile } = useAuth();
  const [displayName, setDisplayName] = useState("");
  const [selectedRole, setSelectedRole] = useState("writer");
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    if (!userProfile) {
      return;
    }

    setDisplayName(userProfile.displayName || "");
    setSelectedRole((userProfile.role || "writer").toLowerCase());
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
        role: selectedRole,
      });
      await refreshProfile();
      setMessage("Role updated successfully.");
    } catch (err) {
      setError(err?.message || "Failed to save role.");
    } finally {
      setSaving(false);
    }
  }

  const email = userProfile?.email || user?.email || "";
  const currentRoleLabel = ({ writer: "Writer", reviewer: "Reviewer", approver: "Approver", admin: "Admin" })[selectedRole] || "Writer";
  const initial = (displayName || email || "U").charAt(0).toUpperCase();

  return (
    <AppLayout initialSelectedNav="Settings">
      <div className="flex  flex-1 flex-col overflow-y-auto px-3 py-4 sm:px-4 md:px-5 lg:px-6 xl:px-8">
        <div className="flex h-full flex-1 flex-col rounded-[26px] border border-[#2d3748] bg-[#111827] p-3 shadow-[0_8px_24px_rgba(2,6,23,0.35)] sm:p-4 md:p-5 lg:p-6">
          <div className="flex items-center justify-between gap-3 pb-4">
            <div>
              <h1 className="text-[2.4rem] font-semibold tracking-[-0.06em] text-slate-100">Role</h1>
              <p className="mt-1 text-[1.05rem] text-slate-400">
                Manage user access and role permissions across the platform.
              </p>
            </div>
          </div>

          <div className="mt-6 grid items-start gap-6 xl:grid-cols-[1.2fr_0.8fr]">
            <section className="flex h-full flex-col rounded-[22px] border border-[#2d3748] bg-[#0f172a] p-4 sm:p-5">
              <div className="flex items-center gap-5">
                <div className="flex items-center justify-center overflow-hidden rounded-full border border-[#374151] bg-[#1e293b] text-[1.3rem] font-semibold text-slate-200">
                  <div className="flex h-20 w-20 items-center justify-center bg-[radial-gradient(circle_at_30%_30%,_#1e293b_0%,_#0f172a_25%,_#111827_100%)] text-slate-100">
                    {initial}
                  </div>
                </div>

                <div className="flex-1">
                  <div className="flex items-center gap-3">
                    <div className="text-[1.1rem] font-semibold text-slate-100">{displayName || "User"}</div>
                  </div>
                  <div className="mt-3 text-[0.96rem] text-slate-400">{email}</div>
                </div>
              </div>

              <div className="mt-6 grid gap-4 md:grid-cols-2">
                <label className="block text-sm font-medium text-slate-300">
                  <span className="mb-2 block">Full Name</span>
                  <input
                    value={displayName}
                    onChange={(e) => setDisplayName(e.target.value)}
                    className="h-12 w-full rounded-xl border border-[#374151] bg-[#111827] px-3 text-base text-slate-100 outline-none focus:border-[#f97316]"
                  />
                </label>

                <label className="block text-sm font-medium text-slate-300">
                  <span className="mb-2 block">Email Address</span>
                  <input
                    value={email}
                    readOnly
                    className="h-12 w-full rounded-xl border border-[#374151] bg-[#111827] px-3 text-base text-slate-100 outline-none"
                  />
                </label>

                <label className="block text-sm font-medium text-slate-300 md:col-span-2">
                  <span className="mb-2 block">Application Role</span>
                  <select
                    value={selectedRole}
                    onChange={(e) => setSelectedRole(e.target.value)}
                    className="h-12 w-full rounded-xl border border-[#374151] bg-[#111827] px-3 text-base text-slate-100 outline-none focus:border-[#f97316]"
                  >
                    {roleOptions.map((roleOption) => (
                      <option key={roleOption} value={roleOption}>
                        {({ writer: "Writer", reviewer: "Reviewer", approver: "Approver", admin: "Admin" })[roleOption]}
                      </option>
                    ))}
                  </select>
                  <span className="mt-2 block text-xs text-slate-500">Update your access level and permissions.</span>
                </label>
              </div>

              <div className="mt-8 rounded-[18px] border border-[#2d3748] bg-[#0b1220] p-4">
                <div className="mb-4 flex items-center justify-between gap-3">
                  <h3 className="text-lg font-semibold text-slate-100">Role permissions</h3>
                  <span className="rounded-full border border-[#f97316]/60 bg-[#f97316]/10 px-2.5 py-1 text-xs font-medium text-[#fdba74]">
                    {currentRoleLabel}
                  </span>
                </div>

                <div className="overflow-hidden rounded-xl border border-[#2d3748]">
                  <table className="min-w-full border-collapse text-left text-sm text-slate-200">
                    <thead className="bg-[#111827] text-slate-300">
                      <tr>
                        <th className="px-3 py-3 font-medium">Role</th>
                        <th className="px-3 py-3 font-medium">Refine</th>
                        <th className="px-3 py-3 font-medium">Request Revision</th>
                        <th className="px-3 py-3 font-medium">Approve</th>
                        <th className="px-3 py-3 font-medium">Publish</th>
                      </tr>
                    </thead>
                    <tbody>
                      {roleOptions.map((roleOption) => {
                        const currentPermissions = permissionMatrix[roleOption];
                        const isSelected = roleOption === selectedRole;
                        return (
                          <tr
                            key={roleOption}
                            className={isSelected ? "bg-[#1f2937] text-slate-100" : "bg-[#0f172a] text-slate-300"}
                          >
                            <td className="border-t border-[#2d3748] px-3 py-3 font-medium">
                              {({ writer: "Writer", reviewer: "Reviewer", approver: "Approver", admin: "Admin" })[roleOption]}
                            </td>
                            <td className="border-t border-[#2d3748] px-3 py-3">
                              {currentPermissions.refine ? "✅" : "—"}
                            </td>
                            <td className="border-t border-[#2d3748] px-3 py-3">
                              {currentPermissions.requestRevision ? "✅" : "—"}
                            </td>
                            <td className="border-t border-[#2d3748] px-3 py-3">
                              {currentPermissions.approve ? "✅" : "—"}
                            </td>
                            <td className="border-t border-[#2d3748] px-3 py-3">
                              {currentPermissions.publish ? "✅" : "—"}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            </section>

            <section className="flex h-full flex-col justify-center rounded-[22px] border border-[#2d3748] bg-[#0f172a] p-4 sm:p-5">
              <h2 className="text-[1.8rem] font-semibold tracking-[-0.05em] text-slate-100">Role Summary</h2>

              <div className="mt-6 space-y-5">
                {message && (
                  <div className="rounded-md bg-emerald-900/40 px-4 py-2 text-sm text-emerald-200">{message}</div>
                )}

                {error && (
                  <div className="rounded-md bg-red-900/40 px-4 py-2 text-sm text-red-200">{error}</div>
                )}

                <div className="rounded-xl border border-[#374151] bg-[#111827] p-4 text-sm text-slate-300">
                  <div className="mb-2 text-slate-400">Current access</div>
                  <div className="text-xl font-semibold text-slate-100">{currentRoleLabel}</div>
                </div>

                <button
                  type="button"
                  onClick={handleSave}
                  disabled={saving}
                  className="mt-2 w-full rounded-xl bg-[#f97316] px-4 py-3 text-base font-semibold text-white shadow-[0_10px_18px_rgba(249,115,22,0.24)] transition hover:bg-[#ea580c] disabled:opacity-60"
                >
                  {saving ? "Saving..." : "Save Role"}
                </button>
              </div>
            </section>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
