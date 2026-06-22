---
name: getting-started-audit
description: "Measure and shorten time-to-first-success — walk the getting-started path from a clean state, time it, rank friction points by where developers drop off, and make a fix-or-document call on each. Use whenever you need to know how good (or bad) onboarding really is."
---

# Skill: Getting-started audit

Measure the one number that decides adoption — time-to-first-success — and find the
friction that's inflating it. Most developers decide in the first ten minutes.

## When to use

- You don't know how long it takes a new developer to get a real result.
- Sign-ups are healthy but activation (first app / retention) is weak.
- Before investing in reach — reach that lands a dev on a broken first-run is waste.

## Procedure

1. **Start from a genuinely clean state** — new account, no cached creds, no
   insider knowledge. Anything you "already know" is a friction point a real
   developer will hit.
2. **Time it to first success.** Record the wall-clock minutes from signup to the
   first real result (first successful call, first working app). That's TTFS.
3. **Log every friction point** — each place you paused, guessed, hit an error, or
   left the page. Note where in the funnel (signup → first call → first app) it
   sits, because friction earlier costs more.
4. **Rank by drop-off impact**, not by how annoying it felt to you. Friction at
   "signup → first call" loses more developers than friction deep in an advanced
   flow.
5. **Make a fix-or-document call per friction point** (tree 2 in
   [`../../knowledge/devrel-engagement-decision-trees.md`](../../knowledge/devrel-engagement-decision-trees.md)):
   product-pain → product-feedback ticket; sound-but-undiscoverable → content task.
6. **Capture it** in the
   [`getting-started-audit`](../../templates/getting-started-audit.md) template.

## Output

A measured TTFS, a ranked friction list, and a fix-or-document disposition per
item — the input to both the content plan and the product-feedback brief.

## Anti-patterns (the hook flags these)

- A getting-started doc with no explicit **first-success milestone**.
- "Improving onboarding" with no TTFS measurement to move.
- Papering over a product flaw with a longer tutorial instead of filing the bug.
