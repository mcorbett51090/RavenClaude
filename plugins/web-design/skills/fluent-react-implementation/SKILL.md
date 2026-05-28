---
name: fluent-react-implementation
description: Implement a Fluent UI v9 + React website end-to-end — set up FluentProvider, turn a brand color into a BrandVariants ramp and light/dark/high-contrast themes (createLightTheme / createDarkTheme), wire design tokens, style with Griffel makeStyles, handle Next.js App Router SSR (the use-client + renderToStyleElements boundary) or Astro islands, build custom components on Fluent primitives, and ship a themed Storybook. Reach for this skill when building or reviewing a Fluent/React site, implementing a brand as a Fluent design language, or debugging Fluent SSR / dark-mode / theming issues. Used by `frontend-implementer` (primary) + `visual-designer` (brand to theme).
---

# Skill: fluent-react-implementation

> The implementation playbook for building **Fluent UI v9 + React** websites and implementing a brand as a **Fluent design language**. Reference: [`../../knowledge/fluent-react-for-web-2026.md`](../../knowledge/fluent-react-for-web-2026.md) (mechanics + dated version/SSR caveats), [`../../knowledge/design-systems-and-component-architecture-2026.md`](../../knowledge/design-systems-and-component-architecture-2026.md) (the headless-vs-styled framing — Fluent is the *styled, themed* choice).

## When to use this (and when not)
- **Use** when the project wants the Microsoft/Fluent aesthetic, or a themeable + accessible + batteries-included React component set you'll **brand via tokens**. Also for Power Pages **React SPA** front-ends in the Microsoft estate (see `power-platform/knowledge/power-pages-2026.md`).
- **Don't** force Fluent on a radically bespoke brand that needs full visual control — use headless (Radix/React Aria) + your own tokens, or Tailwind v4 + shadcn. Theming Fluent into a wildly different look means fighting the system. (Traverse the design-systems "which component foundation?" decision tree first.)

## The 7-step implementation arc

### 1. Confirm the foundation choice
Traverse the design-systems decision tree. If the answer is Fluent, proceed; otherwise hand back to the headless/Tailwind path. Pin the trio (`@fluentui/react-components` + React + the framework) to a verified-working set — Fluent v9 ⨉ React 19 / Next 15 has had real friction; **check the live docs + microsoft/fluentui issues before locking versions**, and record the versions with a retrieval date.

### 2. Brand → theme (the design-language core)
- Take the brand color(s) → generate a **`BrandVariants`** 16-stop ramp (Fluent UI **Theme Designer**, or hand-tune).
- `createLightTheme(brand)` + `createDarkTheme(brand)` → your light/dark themes; keep `webHighContrastTheme` for forced-colors.
- Put the ramp + themes in a single `theme/` module — the token source of truth. Override typography/radius/spacing tokens here where the brand diverges; never hardcode those in components.

### 3. Provider + SSR boundary
- `FluentProvider` at the root with the active theme.
- **Next.js App Router:** a `providers.tsx` with `'use client'` (Griffel `RendererProvider` + `SSRProvider` + `FluentProvider`); `app/layout.tsx` stays a server component and wraps `children`. Emit critical CSS with **`renderToStyleElements`** per the current react.fluentui.dev recipe (verify — it changes across Next versions). Fluent v9 components are **client components** — they can't live in an RSC.
- **Astro/Vite:** Fluent as client islands (`client:load`).
- **Dark mode:** swap the theme prop; persist + honor `prefers-color-scheme`; **set `<body>` background yourself** (FluentProvider doesn't theme body — the classic gotcha).

### 4. Style with Griffel
- `makeStyles` + `mergeClasses`, referencing **`tokens.*`** (semantic), never hex. Enable build-time extraction (`@griffel/webpack-loader` / babel preset) for production perf.

### 5. Compose custom components on Fluent primitives
- Build on Fluent components + slots/composition (not prop-explosion). Only author bespoke primitives when Fluent lacks one. Keep the inherited a11y (keyboard/focus/ARIA) — don't override roles.

### 6. Storybook the themed system
- Stories per component across light/dark/high-contrast; the living catalog + visual-regression + a11y addon. This is the design-language's documentation surface.

### 7. Verify
- A11y (WCAG 2.2 AA floor — `accessibility-review` skill), Core Web Vitals incl. JS weight + INP (`core-web-vitals-tuning` skill — Fluent's CSS-in-JS has a cost; extraction + code-split), responsive/mobile-first, no-hardcoded-values (tokens only), SSR with no FOUC.

## Output
- The `theme/` module (BrandVariants + themes), the provider/SSR setup, token-driven `makeStyles`, custom components, Storybook entries — plus the **pinned, retrieval-dated version trio** and any SSR-recipe caveat. Fill the [`../../templates/design-system-spec.md`](../../templates/design-system-spec.md) with the Fluent specifics.

## Hand-offs
- Brand/visual ambiguity → `visual-designer`. A11y review → `accessibility-auditor`. CWV/JS-weight → `performance-engineer`. A Power Pages React SPA host → `power-platform/power-pages-engineer`. Custom (non-Fluent) headless build → stay in `frontend-implementer` with the design-systems skill.
