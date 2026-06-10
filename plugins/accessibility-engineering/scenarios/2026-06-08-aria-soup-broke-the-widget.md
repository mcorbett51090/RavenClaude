---
scenario_id: 2026-06-08-aria-soup-broke-the-widget
contributed_at: 2026-06-08
plugin: accessibility-engineering
product: design
product_version: "n/a"
scope: likely-general
tags: [aria, semantic-html, screen-reader, name-role-value]
confidence: medium
reviewed: false
---

## Problem

A custom button built from a <div> with role and click handlers was unusable with a keyboard and a screen reader, despite carrying ARIA attributes. The risk: ARIA adds semantics but no behavior, and a wrong or incomplete role/state is worse than no ARIA — "no ARIA is better than bad ARIA" (§3 #4).

## Context

- Surface: a shared component reused across many pages.
- Constraint: a native <button> carries role, focusability, Enter/Space activation, and disabled state for free; a <div> carries none of that and ARIA does not add the behavior (§3 #4).
- The team reasoned that adding role='button' made it accessible.

## Attempts

- Tried: **AT session to characterize the failure** via the assistive-tech path. Outcome: the div was not in the tab order, did not respond to Enter/Space, and announced an incomplete state — classic bad-ARIA symptoms (§3 #4).
- Tried: **evaluated whether a native element fit.** Outcome: a native <button> covered the entire use case — the custom widget existed only for styling, which CSS handles.
- Tried: **replaced the div with a native <button>** and removed the ARIA. Outcome: keyboard operability, focus, and screen-reader announcement worked for free, fixed once in the shared component (§3 #4 #7).

## Resolution

The fix was to **replace the ARIA-decorated div with a native <button> in the shared component** — semantic HTML first, ARIA only where no native element fits. The output was the AT-session diagnosis, the native replacement, and the design-system change to prevent recurrence.

**Action for the next consultant hitting this pattern:** **reach for native HTML before ARIA, and fix it in the shared component.** ARIA adds semantics, never behavior; a native element carries role, state, and keyboard handling for free, and no ARIA beats bad ARIA. See Tree 3 and §3 #4 #7.

Benchmark figures are segment-/region-/date-dependent — treat as `[unverified — training knowledge]` and validate against the client's own data before any deliverable (§3 #8).
