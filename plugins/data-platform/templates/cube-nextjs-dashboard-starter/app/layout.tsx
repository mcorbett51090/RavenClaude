import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Dashboard",
  description: "Cube + Next.js + Tremor dashboard starter (data-platform Case C)",
};

// Runs synchronously, before first paint, and BEFORE React hydrates
// (FORGE dashboard-top1pct P2-18, 2026-09-03) — this is the standard
// Next.js App Router pattern for avoiding a flash-of-wrong-theme: a
// useEffect-driven toggle (see components/ThemeToggle.tsx) can only run
// AFTER hydration, which is one paint too late. localStorage's explicit
// override wins over the system `prefers-color-scheme` default, matching
// web-design's design-tokens-scaffolding skill's "system preference +
// override" rule.
// A static, non-interpolated string constant — no request/user data ever
// reaches this template, so dangerouslySetInnerHTML here carries none of
// the injection risk it would with any dynamic content.
const THEME_INIT_SCRIPT = `
(function () {
  try {
    var stored = localStorage.getItem("theme");
    var dark = stored ? stored === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
    document.documentElement.classList.toggle("dark", dark);
  } catch (e) {}
})();
`;

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        {/* eslint-disable-next-line react/no-danger -- see THEME_INIT_SCRIPT's own comment for why this must be inline, not a module import */}
        <script dangerouslySetInnerHTML={{ __html: THEME_INIT_SCRIPT }} />
      </head>
      <body>{children}</body>
    </html>
  );
}
