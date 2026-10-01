// Compatibility entry for legacy project contract checks.
// The application uses the Next.js App Router under src/app, but the root project
// also keeps a direct src/main.jsx entry expected by smoke tests and tooling.

export default function Main() {
  return null;
}
