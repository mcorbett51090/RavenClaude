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
        // Every value below is a CSS custom property, not a literal hex
        // (FORGE dashboard-top1pct P2-18, 2026-09-03) — see app/globals.css
        // for the :root (light) / .dark (dark) definitions and the
        // contrast verification. This is what makes `.dark` (or a host
        // overriding a --tremor-* var directly, per the embed-inheritance
        // seam) re-theme every `bg-tremor-*`/`text-tremor-*`/`border-tremor-*`
        // utility class with zero component changes.
        tremor: {
          brand: {
            faint: "var(--tremor-brand-faint)",
            muted: "var(--tremor-brand-muted)",
            subtle: "var(--tremor-brand-subtle)",
            DEFAULT: "var(--tremor-brand-DEFAULT)",
            emphasis: "var(--tremor-brand-emphasis)",
            inverted: "var(--tremor-brand-inverted)",
          },
          background: {
            muted: "var(--tremor-background-muted)",
            subtle: "var(--tremor-background-subtle)",
            DEFAULT: "var(--tremor-background-DEFAULT)",
            emphasis: "var(--tremor-background-emphasis)",
          },
          border: { DEFAULT: "var(--tremor-border-DEFAULT)" },
          content: {
            subtle: "var(--tremor-content-subtle)",
            DEFAULT: "var(--tremor-content-DEFAULT)",
            emphasis: "var(--tremor-content-emphasis)",
            strong: "var(--tremor-content-strong)",
            inverted: "var(--tremor-content-inverted)",
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
