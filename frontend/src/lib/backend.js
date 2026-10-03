export function getBackendUrl() {
  const configuredUrl = (
    process.env.NEXT_PUBLIC_BACKEND_URL ||
    process.env.BACKEND_URL ||
    process.env.NEXT_PUBLIC_API_BASE ||
    process.env.API_BASE ||
    "http://localhost:8000"
  )?.trim?.();

  const backendUrl = (configuredUrl || "http://localhost:8000").replace(/\/$/, "");

  if (
    typeof window !== "undefined" &&
    !process.env.NEXT_PUBLIC_BACKEND_URL &&
    !process.env.BACKEND_URL &&
    !process.env.NEXT_PUBLIC_API_BASE &&
    !process.env.API_BASE
  ) {
    console.warn(
      "[gitlab-ai-content-engine] No backend URL is configured. Set NEXT_PUBLIC_BACKEND_URL in the deployment environment or defaulting to localhost:8000."
    );
  }

  return backendUrl;
}
