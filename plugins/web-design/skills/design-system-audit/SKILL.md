---
name: design-system-audit
description: Audit an existing brand / design system for consistency, completeness, token coverage, dark-mode readiness. Used by `visual-designer` (primary) + `frontend-implementer` (token-to-code wiring).
---

# Skill: design-system-audit

**Purpose:** Audit an existing brand / design system for consistency, completeness, token coverage, dark-mode readiness. Used by `visual-designer` (primary) and `frontend-implementer` (token-to-code wiring).

## When to use

- Site / app has visible drift (different blues, different button styles, different spacing)
- Pre-redesign assessment ("what's our actual current system?")
- Dark-mode rollout planning
- Component-library audit
- Onboarding a new brand or sub-brand

## The audit dimensions

For each dimension, score: ✅ consistent / ⚠️ partial / 🔴 inconsistent.

### 1. Color

- Brand color used consistently across surfaces
- Functional colors (success / warning / danger / info) clearly distinct
- Neutral scale: continuous progression (9-step or 11-step), no gaps
- Color used semantically (`color.text.primary`) not raw (`color.gray.500`)
- Contrast ratios ≥ 4.5:1 for body, ≥ 3:1 for UI components
- Dark-mode pair exists for every light-mode color (or documented exception)

### 2. Typography

- Type scale (8-step typical): `display`, `h1`, `h2`, `h3`, `body`, `body-small`, `caption`, `label`
- One font for display, one for body (max two display)
- Weight palette: usually 400 / 600 / 700; never every weight loaded
- Line-height system: tight for headings, comfortable for body
- Font-loading strategy: subsets, `font-display`, preloads on critical fonts

### 3. Spacing

- Geometric scale: 4 / 8 / 12 / 16 / 24 / 32 / 48 / 64 (or `8pt` system)
- No off-scale values in production
- Negative space respected in layouts

### 4. Layout

- Grid system documented (12-column desktop standard; 4 mobile typical)
- Breakpoints documented (sm / md / lg / xl with definitions)
- Max content widths defined
- Container queries used where supported (or media-query fallback)

### 5. Radius & elevation

- Radius scale (none / sm / md / lg / full) documented
- Elevation / shadow scale documented (0 / 1 / 2 / 3 / overlay)
- Consistent application (cards at `sm`, modals at `lg`, etc.)

### 6. Motion

- Timing functions: ease-out (entries) / ease-in (exits) / ease-in-out (through-states)
- Duration scale (100 / 200 / 300 / 500ms)
- `prefers-reduced-motion` fallbacks present

### 7. Iconography

- Icon set documented (single source, single visual style)
- Sizing scale (16 / 20 / 24 / 32)
- Color treatment consistent (currentColor preferred)

### 8. Components

- Button: variants × states × sizes documented + implemented consistently
- Input: variants × states × sizes
- Card, navigation, modal, tabs, accordion — each has a spec + an implementation

### 9. Tokens layer

- Primitive tokens defined (raw values)
- Semantic tokens defined (use-cases consuming primitives)
- Components consume **semantic** tokens, not primitives
- Token build pipeline (JSON → CSS variables / framework consumption)
- Dark-mode token swaps via semantic re-pointing, not component overrides

### 10. Documentation

- Living style guide (Storybook / dedicated docs site)
- Component docs include: anatomy, states, accessibility notes, usage do's-and-don'ts
- Decision log for non-obvious choices

## Output

| Dimension | Score | Findings | Severity (P0 / P1 / P2) |
|---|---|---|---|

Plus:
- **Top 5 fixes** by leverage (fixing N components vs. fixing token layer once)
- **Token-rationalization opportunities** (drop unused, consolidate redundant)
- **Dark-mode readiness gap** (if applicable)
- **Recommendation:** keep / refresh / rebuild

## Severity

- **P0** — system fails consistency at the consumer-visible level (different greens on same page); fix before next launch
- **P1** — token layer drifts from components; fix before next major feature
- **P2** — improvable; not a current visible problem

## Anti-patterns the audit catches

- Components consuming primitive tokens directly
- "Brand blue" with 4 different hex values across the codebase
- Spacing values outside the scale
- A "design system" that's actually a screenshot library
- Dark mode added by global `filter: invert()`
- Storybook stories that don't reflect production reality

## See also

- Template: [`../../templates/design-system-spec.md`](../../templates/design-system-spec.md)
- Agent: [`../../agents/visual-designer.md`](../../agents/visual-designer.md)
- Agent: [`../../agents/frontend-implementer.md`](../../agents/frontend-implementer.md)
