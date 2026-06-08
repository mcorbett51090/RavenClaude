---
description: "Design an accessible-by-default component pattern, semantic HTML first and ARIA only where needed. Reach for this on a design-system or component question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Design accessible pattern

You are running `/accessibility-engineering:design-accessible-pattern` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Reach for native first — A native element carries role, state, and keyboard behavior for free (§3 #4).
2. Add ARIA only where needed — When no native element fits, apply correct role/state/value and re-implement keyboard behavior (§3 #4).
3. Bake in contrast and focus — Contrast-checked tokens via `accessibility_calc.py contrast`, visible focus, and adequate target size (§3 #5 #7).
4. Ship it to the design system — Into the shared component and definition-of-done so the fix prevents recurrence (§3 #7).

## Output
A semantic-first, accessible-by-default pattern in the design system that prevents defects rather than patching them. See [`../skills/design-accessible-pattern/SKILL.md`](../skills/design-accessible-pattern/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No user PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
