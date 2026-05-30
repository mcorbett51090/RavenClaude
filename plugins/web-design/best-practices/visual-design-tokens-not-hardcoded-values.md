# Route every design decision through a token, never a hardcoded value

**Status:** Absolute rule — color, type, spacing, radius, shadow, and motion all flow through named tokens. A hardcoded `#3b82f6` or `margin: 11px` in a component is a bug (house opinions #4, #12).

**Domain:** Design systems / Tokens

**Applies to:** `web-design`

---

## Why this exists

A design system stays coherent because every decision has **one source of truth** (house opinion #12) and components consume that source rather than re-deciding locally. Hardcoded values are how a system drifts: the same blue gets typed five slightly-different ways, dark mode becomes impossible because there's no layer to swap, and contrast is re-litigated per component instead of verified once. Tokens turn theming, dark mode, and contrast into properties of one layer. The team enforces this mechanically — the `check-web-anti-patterns.sh` hook flags hardcoded hex in CSS/JSX outside the token files.

## How to apply

Define **primitive** tokens (raw scale values) once, derive **semantic** tokens (role-named) from them, and have components consume only the semantic layer. Build color scales in `oklch()` so contrast steps are predictable.

```css
@theme {
  /* Primitive layer — the raw ramp, defined once */
  --color-blue-500: oklch(0.55 0.18 250);
  --space-1: 0.25rem; --space-2: 0.5rem; --space-4: 1rem; --space-6: 1.5rem;
  --radius-md: 0.5rem;

  /* Semantic layer — what components actually consume */
  --color-action: var(--color-blue-500);
  --color-text: oklch(0.22 0.02 250);
  --color-surface: oklch(0.99 0 0);
}
```

```css
/* Component consumes the semantic token — never a raw hex, never a magic number */
.btn-primary {
  background: var(--color-action);
  color: var(--color-surface);
  padding-block: var(--space-2);
  padding-inline: var(--space-4);
  border-radius: var(--radius-md);
}
```

**Do:**
- Split primitive vs semantic; components read semantic tokens (`--color-action`, not `--color-blue-500`).
- Keep the token defined in one place, documented in one place, consumed everywhere (house opinion #12).
- Mirror semantic tokens for dark mode instead of inverting colors ad hoc.

**Don't:**
- Inline a hex, a one-off spacing value, or a custom font size in a component (the hook catches hex).
- Use a primitive token directly in a component (`--color-gray-500` for body text) — that defeats the semantic layer.
- Fork a token "just for this one screen" — that *is* the drift the rule prevents.

## Edge cases / when the rule does NOT apply

- **One-off prototype / spike** not entering the design system — fine to hardcode, but it must not graduate to production without tokenization.
- **Truly contextual values** (e.g. a `calc()` derived from container size) aren't tokens — but the inputs to the calc should be.
- **Fluid type/space** uses `clamp()` whose min/max ends are tokens (see [`./frontend-fluid-type-and-space.md`](./frontend-fluid-type-and-space.md)).

## See also

- [`./visual-color-contrast-is-a-constraint.md`](./visual-color-contrast-is-a-constraint.md) — contrast verified once, in the token layer
- [`./frontend-fluid-type-and-space.md`](./frontend-fluid-type-and-space.md) — fluid scales still terminate in tokens
- [`../knowledge/web-design-decision-trees.md`](../knowledge/web-design-decision-trees.md) — "Design token / system vs ad-hoc" tree
- [`../knowledge/modern-css-2026.md`](../knowledge/modern-css-2026.md) — `oklch()`, Tailwind v4 `@theme`, tokens as single source of truth
- [`../agents/visual-designer.md`](../agents/visual-designer.md) (defines tokens), [`../agents/frontend-implementer.md`](../agents/frontend-implementer.md) (wires them)

## Provenance

Distilled from house opinions #4 (design tokens, not hardcoded values) and #12 (one source of truth per decision), the `visual-designer` opinions (semantic tokens drive components; scales are non-negotiable), the `check-web-anti-patterns.sh` hardcoded-hex check, and the token guidance in `modern-css-2026.md` + `design-systems-and-component-architecture-2026.md` (retrieved 2026-05-28).

---

_Last reviewed: 2026-05-30 by `claude`_
