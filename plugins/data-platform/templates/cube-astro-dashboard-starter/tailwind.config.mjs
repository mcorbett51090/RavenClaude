/** @type {import('tailwindcss').Config} */
// Same Tremor color-scale extension as the Next.js starter's
// tailwind.config.ts — see that file for the source (Tremor's own install
// docs, "Getting started" -> framework-specific config).
export default {
  content: [
    "./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}",
    "./node_modules/@tremor/**/*.{js,ts,jsx,tsx}",
  ],
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
    { pattern: /^(bg|text|border)-(blue|emerald|violet|amber|gray)-(50|100|500|600|700)$/ },
  ],
  plugins: [],
};
