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
      <body className="min-h-screen text-white">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}