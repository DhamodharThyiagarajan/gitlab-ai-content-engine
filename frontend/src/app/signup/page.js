"use client";

import { useEffect, useState } from "react";
import { FaGoogle } from "react-icons/fa";
import { FiEye, FiEyeOff, FiFileText, FiZap, FiShield, FiHome, FiArrowRight } from "react-icons/fi";
import {
  createUserWithEmailAndPassword,
  signInWithPopup,
  updateProfile,
} from "firebase/auth";
import { auth, googleProvider } from "../../../firebase";
import { createUserProfile, ensureUserProfile } from "@/lib/firebase/users";
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

export default function SignupPage() {
  const router = useRouter();
  const { user, loading: authLoading } = useAuth();
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!authLoading && user) {
      router.replace("/dashboard");
    }
  }, [authLoading, user, router]);

  async function completeSignUp(credential, displayName) {
    if (displayName) {
      await updateProfile(credential.user, { displayName });
    }

    await createUserProfile(credential.user.uid, {
      email: credential.user.email ?? email,
      displayName: displayName || credential.user.displayName || "",
    });

    router.push("/dashboard");
  }

  async function handleEmailSignup() {
    setError("");

    if (!fullName || !email || !password || !confirmPassword) {
      setError("Please fill in all fields");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    if (password.length < 6) {
      setError("Password must be at least 6 characters");
      return;
    }

    setLoading(true);
    try {
      const credential = await createUserWithEmailAndPassword(auth, email, password);
      await completeSignUp(credential, fullName);
    } catch (err) {
      setError(err?.message || "Account creation failed");
    } finally {
      setLoading(false);
    }
  }

  async function handleGoogleSignup() {
    setError("");
    setLoading(true);
    try {
      const credential = await signInWithPopup(auth, googleProvider);
      await ensureUserProfile(credential.user);
      router.push("/dashboard");
    } catch (err) {
      setError(err?.message || "Google sign-up failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-[88vh] w-full flex-col justify-center bg-[#0d1117] text-white lg:flex-row">
      <section className="relative flex w-full flex-col justify-center overflow-hidden bg-[#f56d2a] px-6 pb-8 pt-6 text-white md:px-10 md:pb-10 md:pt-8 lg:max-w-[55%] lg:px-16 lg:pt-10">
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
            Build Better
            <br />
            Docs with AI
          </h1>

          <p className="mt-6 max-w-[620px] text-base leading-[1.6] text-white/85 md:mt-8 md:text-[1.05rem] lg:text-[1.2rem]">
            Create polished product documentation, release notes, and onboarding content
            faster with an AI-powered workspace built for teams.
          </p>

          <div className="mt-8 space-y-4 md:mt-10 md:space-y-5">
            <Feature icon={<FiFileText />} text="AI Generated Documentation" />
            <Feature icon={<FiZap />} text="Smart Multi-Agent Workflows" />
            <Feature icon={<FiShield />} text="Secure Team Collaboration" />
          </div>
        </div>
      </section>

      <section className="flex w-full items-center justify-center bg-[#f3f2f1] p-4 md:p-5 lg:max-w-[45%] lg:p-8">
        <div className="w-full max-w-[520px] rounded-[26px] border border-[#e7e3df] bg-[#f9f8f7]/90 p-5 shadow-[0_12px_36px_rgba(31,24,20,0.08)] backdrop-blur-sm md:rounded-[30px] md:p-6 lg:p-8">
          <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-[22px] bg-[#fef2eb] shadow-[inset_0_0_0_1px_rgba(245,109,42,0.12)]">
            <svg viewBox="0 0 24 24" className="h-10 w-10 fill-none stroke-[#f56d2a] stroke-[1.8]" aria-hidden="true">
              <path d="M7.5 3.75h7.25l5 5v10.5A2.25 2.25 0 0 1 17.5 21.5h-10A2.25 2.25 0 0 1 5.25 19.25V6A2.25 2.25 0 0 1 7.5 3.75Z" />
              <path d="M14.75 3.75V9h5" />
              <path d="M8.5 12.5h7M8.5 16h7" />
            </svg>
          </div>

          <h2 className="mt-6 text-center text-4xl font-bold tracking-[-0.05em] text-[#1a1d21] sm:text-[3rem]">
            Create Account <span aria-label="sparkles">✨</span>
          </h2>
          <p className="mt-2 text-center text-lg text-[#5c5e61]">Sign up to get started</p>

          <div className="mt-6 space-y-4">
            <div>
              <label className="mb-2 block text-base font-medium text-[#2d3136]">
                Full Name
              </label>
              <input
                id="fullName"
                type="text"
                placeholder="Enter your full name"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full rounded-xl border border-[#d9d5d2] bg-[#f1efee] px-4 py-3.5 text-base text-[#3a3d40] placeholder:text-[#81868c] outline-none transition focus:border-[#f56d2a] focus:bg-white focus:ring-4 focus:ring-[#f56d2a]/10"
              />
            </div>

            <div>
              <label className="mb-2 block text-base font-medium text-[#2d3136]">
                Email Address
              </label>
              <input
                id="email"
                type="email"
                placeholder="Enter your email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full rounded-xl border border-[#d9d5d2] bg-[#f1efee] px-4 py-3.5 text-base text-[#3a3d40] placeholder:text-[#81868c] outline-none transition focus:border-[#f56d2a] focus:bg-white focus:ring-4 focus:ring-[#f56d2a]/10"
              />
            </div>

            <div>
              <label className="mb-2 block text-base font-medium text-[#2d3136]">
                Password
              </label>
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  placeholder="Create a password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full rounded-xl border border-[#d9d5d2] bg-[#f1efee] px-4 py-3.5 pr-12 text-base text-[#3a3d40] placeholder:text-[#81868c] outline-none transition focus:border-[#f56d2a] focus:bg-white focus:ring-4 focus:ring-[#f56d2a]/10 appearance-none"
                />
                <button
                  type="button"
                  aria-label={showPassword ? "Hide password" : "Show password"}
                  onClick={() => setShowPassword((value) => !value)}
                  className="absolute inset-y-0 right-4 flex items-center text-[#7d7f83] transition hover:text-[#f56d2a]"
                >
                  {showPassword ? <FiEyeOff size={18} /> : <FiEye size={18} />}
                </button>
              </div>
            </div>

            <div>
              <label className="mb-2 block text-base font-medium text-[#2d3136]">
                Confirm Password
              </label>
              <div className="relative">
                <input
                  id="confirmPassword"
                  type={showConfirmPassword ? "text" : "password"}
                  placeholder="Confirm your password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="w-full rounded-xl border border-[#d9d5d2] bg-[#f1efee] px-4 py-3.5 pr-12 text-base text-[#3a3d40] placeholder:text-[#81868c] outline-none transition focus:border-[#f56d2a] focus:bg-white focus:ring-4 focus:ring-[#f56d2a]/10 appearance-none"
                />
                <button
                  type="button"
                  aria-label={showConfirmPassword ? "Hide confirm password" : "Show confirm password"}
                  onClick={() => setShowConfirmPassword((value) => !value)}
                  className="absolute inset-y-0 right-4 flex items-center text-[#7d7f83] transition hover:text-[#f56d2a]"
                >
                  {showConfirmPassword ? <FiEyeOff size={18} /> : <FiEye size={18} />}
                </button>
              </div>
            </div>
          </div>

          {error && (
            <div className="mt-4 rounded-md bg-red-50 px-4 py-2 text-sm text-red-700">
              {error}
            </div>
          )}

          <button
            onClick={handleEmailSignup}
            type="button"
            disabled={loading}
            className="mt-7 flex w-full items-center justify-center gap-2 rounded-xl bg-[#f56d2a] px-5 py-4 text-xl font-bold text-white shadow-[0_10px_20px_rgba(245,109,42,0.28)] transition hover:bg-[#eb6528] hover:cursor-pointer focus:outline-none focus:ring-4 focus:ring-[#f56d2a]/30 disabled:opacity-60"
          >
            {loading ? "Creating account..." : "Create Account"}
            <FiArrowRight />
          </button>

          <button
            onClick={handleGoogleSignup}
            type="button"
            disabled={loading}
            className="mt-6 flex w-full items-center justify-center gap-3 rounded-xl border border-[#d9d5d2] bg-white px-4 py-3.5 text-base font-semibold text-[#2d3136] shadow-sm transition hover:bg-[#f7f5f4] hover:cursor-pointer focus:outline-none focus:ring-4 focus:ring-[#f56d2a]/10 disabled:opacity-60"
          >
            <FaGoogle className="text-[#EA4335]" />
            Continue with Google
          </button>

          <div className="mt-6 flex items-center gap-4 text-[#7b7d80]">
            <div className="h-px flex-1 bg-[#d7d1ce]" />
            <span className="text-sm font-medium uppercase tracking-[0.18em]">OR</span>
            <div className="h-px flex-1 bg-[#d7d1ce]" />
          </div>

          <p className="mt-8 text-center text-lg text-[#4b4f52]">
            Already have an account?{" "}
            <Link href="/login" className="font-semibold text-[#f56d2a] hover:text-[#e35e1d] hover:underline">
              Log In
            </Link>
          </p>

          <Link
            href="/"
            className="mt-6 flex w-full items-center justify-center gap-2 rounded-xl border border-[#d9d5d2] bg-white/50 px-4 py-3 text-base font-medium text-[#2d3136] shadow-sm transition hover:bg-white focus:outline-none focus:ring-4 focus:ring-[#f56d2a]/10"
          >
            <FiHome />
            Back to Home
          </Link>
        </div>
      </section>
    </main>
  );
}
