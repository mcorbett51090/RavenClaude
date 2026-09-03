import type { Config } from "tailwindcss";

// The tremor.* color-scale extension below is kept even though @tremor/react
// itself was removed (FORGE dashboard-top1pct P1-7, 2026-09-03) — components/ui/
// (the local Tremor Raw-style replacement) still uses these tokens, and they
// were always plain Tailwind config, never a dependency on the npm package.
const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        tremor: {
          brand: {
            faint: "#eff6ff",
            muted: "#bfdbfe",
            subtle: "#60a5fa",
            DEFAULT: "#3b82f6",
            emphasis: "#1d4ed8",
            inverted: "#ffffff",
          },
          background: {
            muted: "#f9fafb",
            subtle: "#f3f4f6",
            DEFAULT: "#ffffff",
            emphasis: "#374151",
          },
          border: { DEFAULT: "#e5e7eb" },
          content: {
            subtle: "#9ca3af",
            DEFAULT: "#6b7280",
            emphasis: "#374151",
            strong: "#111827",
            inverted: "#ffffff",
          },
        },
      },
    },
  },
  safelist: [
    {
      pattern: /^(bg|text|border)-(blue|emerald|violet|amber|gray)-(50|100|500|600|700)$/,
    },
  ],
  plugins: [],
};

export default config;
