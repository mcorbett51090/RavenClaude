---
name: design-accessible-pattern
description: "Design an accessible-by-default component pattern, semantic HTML first and ARIA only where needed. Reach for this on a design-system or component question."
---

# Skill: Design accessible pattern

Reaching for ARIA when a native element fits adds risk and behavior you have to re-implement; no ARIA beats bad ARIA (§3 #4).

## Step 1 — Reach for native first
A native element carries role, state, and keyboard behavior for free (§3 #4).

## Step 2 — Add ARIA only where needed
When no native element fits, apply correct role/state/value and re-implement keyboard behavior (§3 #4).

## Step 3 — Bake in contrast and focus
Contrast-checked tokens via `accessibility_calc.py contrast`, visible focus, and adequate target size (§3 #5 #7).

## Step 4 — Ship it to the design system
Into the shared component and definition-of-done so the fix prevents recurrence (§3 #7).

## Output
A semantic-first, accessible-by-default pattern in the design system that prevents defects rather than patching them.
