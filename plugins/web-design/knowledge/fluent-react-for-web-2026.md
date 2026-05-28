# Fluent UI v9 + React for the web (2026)

**Last reviewed:** 2026-05-28 · **Confidence:** medium-high — Fluent v9 + React 19 / Next 15 compatibility is fast-moving; pin versions + verify SSR recipe against the current docs (flagged inline). Sources: react.fluentui.dev, fluent2.microsoft.design, microsoft/fluentui GitHub, Griffel docs.
**Owner:** `frontend-implementer` (build) + `visual-designer` (the brand→theme mapping). **Builds on** [`design-systems-and-component-architecture-2026.md`](design-systems-and-component-architecture-2026.md) (the headless-vs-styled framing — Fluent is the *styled, themed* choice) and [`modern-web-stacks-2026.md`](modern-web-stacks-2026.md) (RSC/SSR). The shared Fluent-v9 version source with PCF is [`../../power-platform/knowledge/pcf-react-fluent-platform-libraries.md`](../../power-platform/knowledge/pcf-react-fluent-platform-libraries.md).

## What Fluent UI v9 is (for websites)
`@fluentui/react-components` — Microsoft's design system implemented in React, styled with **Griffel** (atomic CSS-in-JS), themed via **design tokens**. It implements the **Fluent 2** design language (fluent2.microsoft.design). Use it when the project wants the Microsoft aesthetic *or* a themeable, batteries-included, accessible component set (the **styled** branch of the design-systems decision tree). For a highly bespoke brand with full visual control, prefer a **headless** lib + your own tokens instead — Fluent shines when you'll *theme* it, not fight it.

## The four pillars
1. **`FluentProvider`** — the root; publishes the theme via React context to every v9 component. Wrap the app once: `<FluentProvider theme={webLightTheme}>`.
2. **Design tokens** — semantic, not raw: `tokens.colorNeutralBackground1`, `tokens.spacingHorizontalM`, `tokens.borderRadiusMedium`, typography ramp tokens. Components + your `makeStyles` reference **tokens**, never hex (house opinion #4). Switching theme re-maps tokens; components don't change.
3. **Themes + brand ramp** — built-in `webLightTheme` / `webDarkTheme` (+ `webHighContrastTheme`). **To brand it:** define **`BrandVariants`** (a 16-stop ramp, `10`→`160`) from your brand color, then `createLightTheme(brand)` + `createDarkTheme(brand)`. Generate the ramp with the **Fluent UI Theme Designer** (react.fluentui.dev) from a single brand hex. This is the core of *implementing a design language in Fluent*.
4. **Griffel styling** — `makeStyles` + `mergeClasses` (from `@fluentui/react-components` / `@griffel/react`); atomic, deterministic, token-referencing. For production, enable **build-time extraction** (`@griffel/webpack-loader` / babel preset) to cut runtime cost.

## Dark mode (and the body gotcha)
Swap the `theme` prop on `FluentProvider` (`webLightTheme` ↔ `webDarkTheme`, or your branded pair). Persist the user choice + honor `prefers-color-scheme`. **Known gotcha:** `FluentProvider` themes its subtree but **not** `<body>` — set the page background yourself (e.g. apply `colorNeutralBackground1` to `body`, or a top-level FluentProvider wrapping everything) or you get a mismatched body bg (microsoft/fluentui #23626). High-contrast: ship `webHighContrastTheme` for forced-colors users (house opinion #1 + #13).

## SSR / Next.js App Router (the integration reality)
Fluent v9 relies on the React **Context API**, so v9 components are **client components** — they **cannot render inside an RSC**. Pattern:
- Make a `providers.tsx` with `'use client'` that sets up the Griffel `RendererProvider` + `SSRProvider` + `FluentProvider`; wrap `children` in it from `app/layout.tsx` (layout stays a server component).
- Use **`renderToStyleElements`** to emit critical Griffel CSS during SSR (avoids FOUC) — follow the current "SSR with Next.js App Router" recipe in react.fluentui.dev (the recipe has changed across Next versions — **verify against the live doc**).
- **React 19 / Next 15:** there were real compatibility frictions (microsoft/fluentui #33327, #32832, #33850 — large JS, RSC-forbidden, peer-deps). **Pin `@fluentui/react-components` + React + Next to a verified-working trio and check the issue tracker before upgrading.** (Cite the versions with a retrieval date — house opinion: volatile.)
- Astro/Vite: Fluent v9 works as client islands (`client:load`); same `'use client'`-equivalent boundary.

## Implementing a design language in Fluent (the workflow)
1. **Brand → ramp:** brand hex → `BrandVariants` (Theme Designer) → `createLightTheme`/`createDarkTheme`. Keep the ramp + themes in a `theme/` module (the token source of truth).
2. **Map your design tokens → Fluent tokens** where you diverge (typography ramp, radius, spacing) via theme overrides; don't hardcode in components.
3. **Custom components on Fluent primitives:** compose Fluent components + `makeStyles` referencing tokens; reach for **slots**/composition, not prop-explosion (design-systems doc). Only build bespoke when Fluent lacks the primitive.
4. **Storybook** the themed components (light/dark/high-contrast) as the living catalog + visual-regression.
5. **A11y is inherited** from Fluent primitives — keep it (keyboard, focus, ARIA); don't override roles.

## When NOT to use Fluent
- A non-Microsoft brand wanting a *distinctive* look with full control → headless (Radix/React Aria) + your tokens, or Tailwind v4 + shadcn (see the design-systems decision tree). Theming Fluent into a radically different aesthetic is possible but you fight the system.
- A mostly-static content/marketing site with little interactive UI → the JS weight of a component lib may not pay off; consider plain semantic HTML + tokens (house opinion #2 perf budget).

## Sources (retrieved 2026-05-28)
[Fluent UI React v9 docs + Theme Designer](https://react.fluentui.dev), [Fluent 2 design language](https://fluent2.microsoft.design), Griffel docs, microsoft/fluentui GitHub (SSR + React 19 issues), the shared PCF version source. Pin + re-verify on the Researcher sweep — Fluent/React/Next compatibility dates quickly.
