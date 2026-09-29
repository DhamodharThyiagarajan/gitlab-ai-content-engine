"use client";

import { useState } from "react";
import {
  FiBookOpen,
  FiFileText,
  FiImage,
  FiLink2,
  FiMessageSquare,
  FiPlus,
  FiShield,
  FiZap,
} from "react-icons/fi";
import AppLayout from "@/components/layout/AppLayout";

const templateCards = [
  {
    label: "Documentation",
    description: "Technical guides, user manuals, setup instructions",
    tone: "blue",
    icon: FiBookOpen,
  },
  {
    label: "Release Notes",
    description: "Product updates, feature releases, bug fixes",
    tone: "orange",
    icon: FiFileText,
  },
  {
    label: "API Documentation",
    description: "Endpoints, schema details, integration guidance",
    tone: "purple",
    icon: FiShield,
  },
  {
    label: "Knowledge Article",
    description: "How-to articles, FAQs, onboarding content",
    tone: "green",
    icon: FiImage,
  },
  {
    label: "Blog Post",
    description: "Product stories, announcements, thought leadership",
    tone: "orange",
    icon: FiMessageSquare,
  },
  {
    label: "Custom Content",
    description: "Start from scratch with your own prompt",
    tone: "blue",
    icon: FiPlus,
  },
];

const tabStyles = {
  active: "border-b-2 border-[#f56d2a] bg-[#fffaf7] text-[#1f2328]",
  inactive: "text-[#58606d] hover:text-[#1f2328]",
};

export default function CreateContentPage() {
  const [selectedTab, setSelectedTab] = useState("Templates");
  const [prompt, setPrompt] = useState("");

  return (
    <AppLayout initialSelectedNav="Create Content">
      <div className="max-h-[calc(100vh-12rem)] overflow-y-auto px-3 py-4 sm:px-4 md:px-5 md:py-5 xl:px-6">
        <div className="w-full min-w-0 rounded-[22px] border border-[#f0dfd3] bg-[#f6f2ee] p-4 shadow-[0_2px_12px_rgba(15,23,42,0.02)] sm:p-5 lg:p-6">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="text-sm font-medium text-[#5d6775]">GitLab AI</div>
            <div className="flex w-full min-w-0 items-center gap-2 rounded-full border border-[#e9ddd3] bg-white px-3 py-1.5 text-xs text-[#5f6770] shadow-sm sm:max-w-[420px]">
              <FiLink2 className="h-3.5 w-3.5 shrink-0" />
              <span className="truncate">Search content, jobs, or templates...</span>
            </div>
          </div>

          <div className="mt-5">
            <h1 className="text-2xl font-semibold tracking-[-0.05em] text-[#1f2328] sm:text-[2.2rem]">
              Create Content
            </h1>
          </div>

          <p className="mt-2 max-w-[640px] text-sm text-[#5f646d] sm:text-[1rem]">
            Generate high-quality content using AI. Choose a template or start from scratch.
          </p>

          <div className="mt-5 flex gap-3 border-b border-[#eadfda] pb-2">
            {["Templates", "Custom", "From Existing"].map((tab) => (
              <button
                key={tab}
                type="button"
                onClick={() => setSelectedTab(tab)}
                className={`rounded-t-lg px-3 py-2 text-sm font-medium transition ${
                  selectedTab === tab ? tabStyles.active : tabStyles.inactive
                }`}
              >
                {tab}
              </button>
            ))}
          </div>

          <div className="mt-5 grid min-w-0 grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
            {templateCards.map(({ label, description, tone, icon: Icon }) => {
              const toneMap = {
                blue: "border-[#dfe9ff] bg-[#f6f9ff] text-[#2b4eb0]",
                orange: "border-[#f9e4d0] bg-[#fff9f4] text-[#d46f2c]",
                purple: "border-[#e8dcff] bg-[#f7f3ff] text-[#6c52d8]",
                green: "border-[#d9f3e5] bg-[#f3fdf9] text-[#2d9b6d]",
              };

              return (
                <div
                  key={label}
                  className="flex h-full min-h-[220px] min-w-0 flex-col justify-between rounded-[18px] border border-[#eae0d9] bg-white p-4 shadow-[0_1px_0_rgba(15,23,42,0.02)]"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div
                      className={`flex h-11 w-11 items-center justify-center rounded-xl border ${toneMap[tone]}`}
                    >
                      <Icon className="h-5 w-5" />
                    </div>
                  </div>

                  <div className="mt-5">
                    <h2 className="text-lg font-semibold text-[#1f2328]">{label}</h2>
                    <p className="mt-2 text-sm leading-5 text-[#616a73]">{description}</p>
                  </div>

                  <button
                    type="button"
                    className={`mt-5 inline-flex w-full items-center justify-center rounded-xl border px-3 py-2.5 text-sm font-semibold transition ${
                      tone === "orange"
                        ? "border-[#f5d3ba] bg-[#fff3ea] text-[#d5652a] hover:bg-[#ffefe3]"
                        : "border-[#dfe9ff] bg-[#f5f8ff] text-[#2d4db5] hover:bg-[#edf4ff]"
                    }`}
                  >
                    Use Template
                  </button>
                </div>
              );
            })}
          </div>

          <div className="mt-6 rounded-[18px] border border-[#e8ddd5] bg-white p-4 shadow-[inset_0_0_0_1px_rgba(15,23,42,0.02)]">
            <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
              <div className="text-sm font-medium text-[#4d5561]">Or start with a custom prompt</div>
              <div className="text-xs text-[#7a716a]">0/7000</div>
            </div>

            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              rows={5}
              className="mt-3 w-full resize-none border-0 bg-[#f9f7f5] p-3 text-sm text-[#39414a] placeholder:text-[#867b75] focus:outline-none"
              placeholder="Describe what you want to create..."
            />

            <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex items-center gap-2 text-[#6b6968]">
                <button type="button" className="rounded-lg border border-[#e8dcd4] bg-[#faf7f5] p-2">
                  <FiFileText className="h-4 w-4" />
                </button>
                <button type="button" className="rounded-lg border border-[#e8dcd4] bg-[#faf7f5] p-2">
                  <FiLink2 className="h-4 w-4" />
                </button>
              </div>

              <button
                type="button"
                className="inline-flex items-center justify-center gap-2 rounded-xl bg-[#f56d2a] px-4 py-2.5 text-sm font-semibold text-white shadow-[0_10px_18px_rgba(245,109,42,0.22)] transition hover:bg-[#e55f1c] sm:w-auto"
              >
                <FiZap className="h-4 w-4" />
                Generate with AI
              </button>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
