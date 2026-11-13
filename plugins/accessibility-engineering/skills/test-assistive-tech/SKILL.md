---
name: test-assistive-tech
description: "Verify keyboard operability and screen-reader parity hands-on with the assistive technology real users use. Reach for this on a parity question."
---

# Skill: Test assistive tech

Automated tools miss focus order, alt-text meaning, and name/role/value — only AT testing finds them (§3 #2 #3).

## Step 1 — Walk it by keyboard
No traps, visible focus, logical order, every control reachable and operable (§3 #3).

## Step 2 — Test with a screen reader
Name, role, value, state changes, and live-region announcements conveyed correctly (§3 #3).

## Step 2b — Rail and disclosures
On a portal or app shell, also check [`../../knowledge/portal-and-agent-accessibility-2026-11.md`](../../knowledge/portal-and-agent-accessibility-2026-11.md) (§3b):

- The current location is announced. More than one `aria-current` is not, by itself, a failure.
- A disclosure button announces expanded or collapsed (`aria-expanded`) and controls the region named by `aria-controls`.
- Wayfinding is not announced as a menu. `role="menu"` on a nav disclosure is a failure.
- Every primary rail item has a visible text label, and that label is the accessible name (or includes it).

## Step 3 — Cover the AT a population uses
Multiple screen readers/magnification/switch as scope demands; date the AT/browser versions (§3 #8).

## Step 4 — Rank the gaps
Order AT-found defects by user-impact via `accessibility_calc.py remediation`.

## Output
An AT-session report naming the keyboard/screen-reader parity gaps automated tools missed, ranked by user-impact.
