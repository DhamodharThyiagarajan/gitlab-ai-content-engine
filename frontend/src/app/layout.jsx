import "./global.css";
import Providers from "./providers";

export const metadata = {
  title: "GitLab ",
  description:
    "Multi-agent content generation for GitLab release notes, docs, and blogs.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-[#070d18] text-slate-100 antialiased">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}