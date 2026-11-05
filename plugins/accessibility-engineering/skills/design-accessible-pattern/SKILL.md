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

## Step 5 — Portal and app chrome
When the pattern is wayfinding, apply [`../../knowledge/portal-and-agent-accessibility-2026-11.md`](../../knowledge/portal-and-agent-accessibility-2026-11.md) (§3b):

- Persistent visible left rail; every primary item has visible text.
- Mark the current location. Do not require exactly one `aria-current`.
- A disclosure is a `<button>` with `aria-expanded` and `aria-controls`. Wayfinding does not use `role="menu"`.
- Local navigation is visually quieter than the main rail.

## Step 6 — Coding-agent legibility
Apply the same file's provisional practice list, and label it provisional: semantic controls with accessible names, a stable hook you name (do not invent `data-agent`), non-secret state in the URL, confirmation before a destructive action, page text treated as untrusted. Leave WebMCP, hosted MCP, `llms.txt` gates, Cursor rules migrations, and Storybook MCP-for-Astro unimplemented. Those rows are unverified.

## Output
A semantic-first, accessible-by-default pattern in the design system that prevents defects rather than patching them. Chrome follows the solid rail and disclosure rules. Agent-legibility items that came from the unfinished research run stay labeled provisional.
