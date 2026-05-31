---
description: Scaffold a design-token system as the single source of truth — primitive ramps once, role-named semantic tokens components consume, contrast verified in the token layer with oklch lightness ramps, dark-mode mirrors, and fluid clamp() scales whose ends are tokens.
argument-hint: "[the brand/system, e.g. 'tokens for a new marketing site' or 'tokenize this component library']"
---

# Scaffold design tokens

You are running `/web-design:scaffold-design-tokens`. Stand up (or refactor toward) the token system for what the user described (`$ARGUMENTS`), following this plugin's `visual-designer` + `frontend-implementer` discipline. A design system stays coherent because every decision has one source of truth — a hardcoded `#3b82f6` or `margin: 11px` in a component is the drift this prevents.

## When to use this

Setting up a design system, or remediating one that has hardcoded values, drifted blues, or no dark-mode layer. Not for a throwaway prototype not entering the system (fine to hardcode there, but it must tokenize before production).

## Steps

1. **Route every decision through a token** (`visual-design-tokens-not-hardcoded-values`): color, type, spacing, radius, shadow, and motion all flow through named tokens — the `check-web-anti-patterns.sh` hook flags hardcoded hex outside the token files. Token defined once, documented once, consumed everywhere.
2. **Split primitive from semantic** (`visual-design-tokens-not-hardcoded-values`): define primitive ramps (the raw scale) once, derive role-named semantic tokens (`--color-action`, `--color-text`, `--color-surface`) from them, and have components consume *only* the semantic layer — never a primitive (`--color-gray-500` for body text defeats it).
3. **Verify contrast in the token layer with oklch ramps** (`visual-color-contrast-is-a-constraint`): build color scales in `oklch()` so equal lightness reads equally bright and contrast steps are predictable; verify each text/background pair (including muted body, links, hover states) meets 4.5:1 / 3:1 once, in the tokens, not per component.
4. **Mirror semantic tokens for dark mode** (`visual-design-tokens-not-hardcoded-values`): provide a dark-mode mirror of the semantic layer rather than inverting colors ad hoc; honor `forced-colors` with system color keywords where boundaries matter.
5. **Make type and space fluid, with token ends** (`frontend-fluid-type-and-space`): express type/space as `clamp(min, fluid, max)` whose min/max ends are tokens, authored mobile-first; cap body line length around 60-75ch. Reach for container queries when a component must adapt to its slot, not the viewport.

## Guardrails

- Don't fork a token "just for this one screen" — that *is* the drift the rule prevents; one source of truth per decision (house opinion #12).
- AA is the team default contrast floor; state explicitly when you're holding a body-heavy reading surface to AAA (7:1).
- For a Fluent UI v9 brand, the design language is BrandVariants → `createLightTheme`/`createDarkTheme` (see the `fluent-react-implementation` skill); coordinate the token-to-code pipeline (W3C token JSON + Style Dictionary, Tailwind v4 `@theme`) with `frontend-implementer`.
