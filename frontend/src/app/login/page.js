"use client";

import { useEffect, useState } from "react";
import { FaGoogle } from "react-icons/fa";
import { FiEye, FiEyeOff, FiFileText, FiZap, FiShield, FiHome, FiArrowRight } from "react-icons/fi";
import { signInWithPopup, signInWithEmailAndPassword } from "firebase/auth";
import { auth, googleProvider } from "../../../firebase";
import { ensureUserProfile } from "@/lib/firebase/users";
import { useAuth } from "@/hooks/useAuth";
import { useRouter } from "next/navigation";
import Link from "next/link";

function Feature({ icon, text }) {
  return (
    <div className="flex items-center gap-4 text-white">
      <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-white/20 bg-white/10 text-lg text-white shadow-sm">
        {icon}
      </div>
      <span className="text-base font-medium text-white/95">{text}</span>
    </div>
  );
}

export default function LoginPage() {
  const router = useRouter();
  const { user, loading: authLoading } = useAuth();
  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!authLoading && user) {
      router.replace("/dashboard");
    }
  }, [authLoading, user, router]);

  async function completeSignIn(credential) {
    const token = await credential.user.getIdToken();
    console.log("Firebase ID Token:", token);
    await ensureUserProfile(credential.user);
    router.push("/dashboard");
  }

  async function handleGoogleLogin() {
    setError("");
    setLoading(true);
    try {
      const credential = await signInWithPopup(auth, googleProvider);
      await completeSignIn(credential);
    } catch (err) {
      setError(err?.message || "Google sign-in failed");
    } finally {
      setLoading(false);
    }
  }

  async function handleEmailLogin() {
    setError("");
    if (!email || !password) {
      setError("Please enter email and password");
      return;
    }
    setLoading(true);
    try {
      const credential = await signInWithEmailAndPassword(auth, email, password);
      await completeSignIn(credential);
    } catch (err) {
      setError(err?.message || "Email/password sign-in failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen w-full flex-col justify-center bg-[#020817] text-white lg:flex-row">
      <section className="relative flex w-full flex-col justify-center overflow-hidden bg-[#f97316] px-6 pb-8 pt-6 text-white md:px-10 md:pb-10 md:pt-8 lg:max-w-[55%] lg:px-16 lg:pt-10">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,_rgba(255,255,255,0.16),_transparent_35%)]" />
        <div className="relative z-10 flex h-full flex-col justify-center">
          <div className="flex items-center gap-3 text-2xl font-bold text-white sm:text-3xl">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-white/15 bg-white/10 shadow-inner backdrop-blur-sm sm:h-12 sm:w-12">
              <img
                src="/gitlab.jpg"
                alt="GitLab icon"
                className="h-5 w-5 rounded-sm object-cover sm:h-6 sm:w-6"
              />
            </div>
            <span>GitLab</span>
          </div>

          <div className="mt-8 inline-flex w-fit items-center gap-2 rounded-full border border-white/25 bg-white/10 px-4 py-2 text-sm font-medium text-white shadow-sm backdrop-blur-sm md:mt-14 md:text-base">
            <span className="text-base md:text-lg">✦</span>
            AI Powered Documentation
          </div>

          <h1 className="mt-8 max-w-[540px] text-[2.7rem] font-extrabold leading-[0.9] tracking-[-0.06em] text-white md:mt-10 md:text-[4.2rem] lg:text-[7rem]">
            AI Content &amp;
            <br />
            Documentation
            <br />
            Engine
          </h1>

          <p className="mt-6 max-w-[620px] text-base leading-[1.6] text-white/85 md:mt-8 md:text-[1.05rem] lg:text-[1.2rem]">
            Generate release notes, API documentation, technical blogs and onboarding
            guides with powerful AI-driven workflows.
          </p>

          <div className="mt-8 space-y-4 md:mt-10 md:space-y-5">
            <Feature icon={<FiFileText />} text="AI Generated Documentation" />
            <Feature icon={<FiZap />} text="Multi-Agent Workflow" />
            <Feature icon={<FiShield />} text="Secure Team Collaboration" />
          </div>
        </div>
      </section>

      <section className="flex w-full items-center justify-center bg-[#0f172a] p-4 md:p-6 lg:max-w-[45%] lg:p-10">
        <div className="w-full max-w-[520px] rounded-[26px] border border-[#2d3748] bg-[#111827]/90 p-6 shadow-[0_12px_36px_rgba(2,6,23,0.45)] backdrop-blur-sm md:rounded-[32px] md:p-8 lg:p-10">
          <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-[22px] bg-[#1e293b] shadow-[inset_0_0_0_1px_rgba(148,163,184,0.15)]">
            <svg viewBox="0 0 24 24" className="h-10 w-10 fill-none stroke-[#f97316] stroke-[1.8]" aria-hidden="true">
              <path d="M7.5 3.75h7.25l5 5v10.5A2.25 2.25 0 0 1 17.5 21.5h-10A2.25 2.25 0 0 1 5.25 19.25V6A2.25 2.25 0 0 1 7.5 3.75Z" />
              <path d="M14.75 3.75V9h5" />
              <path d="M8.5 12.5h7M8.5 16h7" />
            </svg>
          </div>

          <h2 className="mt-8 text-center text-4xl font-bold tracking-[-0.05em] text-slate-100 sm:text-[3rem]">
            Welcome Back <span aria-label="wave">👋</span>
          </h2>
          <p className="mt-3 text-center text-lg text-slate-400">Login to continue to your account</p>

          <div className="mt-8 space-y-6">
            <div>
              <label className="mb-2 block text-base font-medium text-slate-200">
                Email Address
              </label>
              <input
                id="email"
                type="email"
                placeholder="Enter your email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full rounded-xl border border-[#374151] bg-[#0f172a] px-4 py-3.5 text-base text-slate-100 placeholder:text-slate-500 outline-none transition focus:border-[#f97316] focus:ring-4 focus:ring-[#f97316]/10"
              />
            </div>

            <div>
              <div className="mb-2 flex items-center justify-between gap-4">
                <label className="block text-base font-medium text-slate-200">
                  Password
                </label>
                <button type="button" className="text-sm font-medium text-[#fbbf24] transition hover:text-[#f59e0b] hover:cursor-pointer hover:underline">
                  Forgot password?
                </button>
              </div>
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full rounded-xl border border-[#374151] bg-[#0f172a] px-4 py-3.5 pr-12 text-base text-slate-100 placeholder:text-slate-500 outline-none transition focus:border-[#f97316] focus:ring-4 focus:ring-[#f97316]/10 appearance-none"
                />
                <button
                  type="button"
                  aria-label={showPassword ? "Hide password" : "Show password"}
                  onClick={() => setShowPassword((value) => !value)}
                  className="absolute inset-y-0 right-4 flex items-center text-slate-400 transition hover:text-[#fbbf24]"
                >
                  {showPassword ? <FiEyeOff size={18} /> : <FiEye size={18} />}
                </button>
              </div>
            </div>
          </div>

          {error && (
            <div className="mt-4 rounded-md bg-red-900/40 px-4 py-2 text-sm text-red-200">
              {error}
            </div>
          )}

          <button
            onClick={handleEmailLogin}
            type="button"
            disabled={loading}
            className="mt-8 flex w-full items-center justify-center gap-2 rounded-xl bg-[#f97316] px-5 py-4 text-xl font-bold text-white shadow-[0_10px_20px_rgba(249,115,22,0.28)] transition hover:bg-[#ea580c] hover:cursor-pointer focus:outline-none focus:ring-4 focus:ring-[#f97316]/30 disabled:opacity-60"
          >
            {loading ? "Signing in..." : "Login"}
            <FiArrowRight />
          </button>

          <button
            onClick={handleGoogleLogin}
            type="button"
            disabled={loading}
            className="mt-6 flex w-full items-center justify-center gap-3 rounded-xl border border-[#374151] bg-[#0f172a] px-4 py-3.5 text-base font-semibold text-slate-200 shadow-sm transition hover:bg-[#182335] hover:cursor-pointer focus:outline-none focus:ring-4 focus:ring-[#f97316]/10 disabled:opacity-60"
          >
            <FaGoogle className="text-[#EA4335]" />
            Continue with Google
          </button>

          <div className="mt-8 flex items-center gap-4 text-slate-400">
            <div className="h-px flex-1 bg-[#334155]" />
            <span className="text-sm font-medium uppercase tracking-[0.18em]">OR</span>
            <div className="h-px flex-1 bg-[#334155]" />
          </div>

          <p className="mt-8 text-center text-lg text-slate-300">
            Don&apos;t have an account?{" "}
            <Link href="/signup" className="font-semibold text-[#fbbf24] hover:text-[#f59e0b] hover:underline">
              Sign Up
            </Link>
          </p>

          <Link
            href="/"
            className="mt-6 flex w-full items-center justify-center gap-2 rounded-xl border border-[#374151] bg-[#0f172a] px-4 py-3 text-base font-medium text-slate-200 shadow-sm transition hover:bg-[#182335] focus:outline-none focus:ring-4 focus:ring-[#f97316]/10"
          >
            <FiHome />
            Back to Home
          </Link>
        </div>
      </section>
    </main>
  );
}
