# Use CSS Custom Properties as the Bridge Between Token System and Components

**Status:** Pattern
**Domain:** Web Design — Design tokens / frontend implementation
**Applies to:** `web-design`

---

## Why this exists

A design token system (primitive → semantic → component tokens) is only as useful as its runtime accessibility. CSS custom properties (`--color-primary-500`, `--spacing-md`) are the native browser mechanism that makes tokens consumable at the CSS layer — including in dark mode (`@media (prefers-color-scheme: dark)`), high contrast (`@media (forced-colors: active)`), and future theming variants — without a JavaScript build step. Teams that skip this layer and write token values as hardcoded strings inside JavaScript components lose the ability to override tokens globally (for dark mode, white-labeling, or high-contrast) without rebuilding the JS. This is the structural reason house opinion #4 ("design tokens, not hardcoded values") requires the token-to-component layer to go through custom properties.

## How to apply

**Token architecture layers:**

```css
/* Layer 1: Primitive tokens — raw values */
:root {
  --color-blue-500: #3b82f6;
  --color-red-600: #dc2626;
  --space-4: 1rem;
  --radius-md: 6px;
}

/* Layer 2: Semantic tokens — meaning, not value */
:root {
  --color-action-primary: var(--color-blue-500);
  --color-feedback-error: var(--color-red-600);
  --space-component-gap: var(--space-4);
}

/* Layer 3: Component tokens — scoped overrides (optional) */
.button {
  --button-radius: var(--radius-md);
  --button-bg: var(--color-action-primary);
}

/* Dark mode override — reassign semantic tokens only */
@media (prefers-color-scheme: dark) {
  :root {
    --color-action-primary: #60a5fa;  /* blue-400 in dark */
  }
}
```

**Component CSS consumes semantic tokens, never primitives:**

```css
/* Good */
.button { background: var(--color-action-primary); }

/* Bad — skip semantic layer, brittle */
.button { background: var(--color-blue-500); }

/* Worst — no tokens at all */
.button { background: #3b82f6; }
```

**Do:**
- Define all tokens in `:root` (or a scoped selector for component-level tokens).
- Use semantic tokens in components; use primitive tokens only to define the semantic layer.
- Leverage the cascade: a parent element can override `--color-action-primary` to theme a sub-tree without touching the component CSS.

**Don't:**
- Use CSS custom properties as a substitute for the token *system* (naming discipline matters — a random `--mycolor: blue` is not a token).
- Mix `var(--primitive-token)` and hardcoded values in the same component.
- Forget to define fallbacks for critical tokens: `var(--color-action-primary, #3b82f6)` prevents invisible text if a token is missing.

## Edge cases / when the rule does NOT apply

- **JS-in-CSS design systems** (Styled Components, Griffel/Fluent v9): these systems manage the token layer in JS and inject tokens at the runtime layer. The principle is the same — semantic token consumed by component, primitive defined once — but the mechanism is not CSS custom properties. Don't fight the system's token layer to force CSS custom properties.
- **Legacy browsers without CSS custom property support**: IE11 is below 0.3% global usage `[verify-at-build]`. If it is a target, use a PostCSS plugin to resolve custom properties at build time.

## See also

- [`../agents/visual-designer.md`](../agents/visual-designer.md) — defines the token vocabulary
- [`../agents/frontend-implementer.md`](../agents/frontend-implementer.md) — wires tokens to components in CSS
- [`./visual-design-tokens-not-hardcoded-values.md`](./visual-design-tokens-not-hardcoded-values.md) — the parent rule; this doc covers the CSS custom-property mechanism

## Provenance

Codifies house opinion #4 ("Design tokens, not hardcoded values") and house opinion #12 ("One source of truth per design decision") applied at the CSS layer. CSS custom properties (CSS Variables) specification: W3C CSS Custom Properties Level 1. Design-token architecture from Style Dictionary and W3C Design Tokens Community Group. _Last reviewed: 2026-06-05._

---

_Last reviewed: 2026-06-05 by `claude`_
