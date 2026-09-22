/** @type {import('tailwindcss').Config} */
// The tremor.* color-scale extension below is kept even though @tremor/react
// itself was removed (FORGE dashboard-top1pct P1-7, 2026-09-03) —
// src/components/ui/ (the local Tremor Raw-style replacement) still uses
// these tokens, and they were always plain Tailwind config, never a
// dependency on the npm package. Same extension as the Next.js starter's
// tailwind.config.ts.
export default {
  content: ["./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        // Every value below is a CSS custom property, not a literal hex
        // (FORGE dashboard-top1pct P2-18, 2026-09-03) — see the identical
        // scheme + contrast verification in the Next.js starter's
        // tailwind.config.ts and app/globals.css. Definitions live in
        // src/styles/globals.css.
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
    { pattern: /^(bg|text|border)-(blue|emerald|violet|amber|gray)-(50|100|500|600|700)$/ },
  ],
  plugins: [],
};
