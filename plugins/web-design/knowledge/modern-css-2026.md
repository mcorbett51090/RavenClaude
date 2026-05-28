# Modern CSS (2026)

**Last reviewed:** 2026-05-28 · **Confidence:** medium-high — check Baseline/caniuse before relying on a feature for a specific audience. Sources: MDN + 2026 CSS discourse (retrieval-dated).
**Owner:** `visual-designer` + `frontend-implementer` (complements the `design-tokens-scaffolding` + `design-system-audit` skills).

The CSS capabilities that are **safe to use in 2026** and change how you build — reach for the platform before a library (house opinion: tokens not hardcodes; semantic-first).

## Layout
- **Container queries** (`@container`) — components respond to their **parent's** width, not the viewport. The modern replacement for viewport media queries in component libraries. Pair with **container style queries** for theme-aware components.
- **Subgrid** (`grid-template-*: subgrid`) — a child grid inherits the parent's tracks; finally lets card headers/footers align across a grid regardless of content length. Widely supported in 2026.
- **Logical properties** (`margin-inline`, `padding-block`, `inset`) — RTL/i18n-safe by default; prefer over physical `left/right/top/bottom`.

## Selectors & cascade
- **`:has()`** — the "parent selector"; ~100% support in 2026, production-safe. Enables state-driven styling without JS (e.g. `form:has(:invalid)`).
- **Cascade layers** (`@layer`) — explicit priority order independent of specificity; tame specificity wars and order third-party vs app CSS. (Reduces utility-class bloat + `!important` fights.)
- **CSS nesting** — native (no preprocessor needed for nesting).

## Color
- **`oklch()`** — perceptually-uniform color; equal Lightness *looks* equally bright across hues (unlike HSL), so palettes + accessible contrast ramps are far easier to build. Wider gamut than sRGB. **Prefer `oklch()` for design-token color scales** (then provide an sRGB fallback for old targets). `color-mix()` for programmatic tints/shades.

## Motion & transitions
- **View Transitions API** (`@view-transition` / `document.startViewTransition`) — smooth cross-state and cross-document (MPA) transitions natively; Astro/Next expose it. Always gate behind **`prefers-reduced-motion: reduce`** (house opinion #13).
- `@property` for typed custom properties (animatable gradients/values).

## Tailwind v4 (if the project uses Tailwind)
- **v4** uses the **Rust "Oxide" engine** (much faster builds) and a **CSS-first config** (`@theme` in CSS, not `tailwind.config.js`). Map design tokens into `@theme` so tokens stay the single source of truth (house opinion #4 + #12). Container queries + `:has()` variants are first-class.

## Discipline
- **Tokens, not hardcodes** (#4): color via `oklch()` custom properties / `@theme`; spacing/type/radius/shadow/motion all tokenized.
- **Check Baseline** before shipping a feature to a broad audience; provide graceful fallbacks (`@supports`).
- **No layout shift** (#7): reserve space; container queries don't excuse CLS.

## Sources (retrieved 2026-05-28)
MDN (`oklch()`, View Transitions, `:has()`, container queries, cascade layers, subgrid); 2026 modern-CSS roundups (nickpaolini.com, logrocket, css-tricks); Tailwind v4 docs. Re-verify Baseline status on the Researcher sweep.
