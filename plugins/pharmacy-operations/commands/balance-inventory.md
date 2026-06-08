---
description: "Read days-on-hand as tied-up cash vs stockout risk by class, handling specialty/340B/refrigerated distinctly. Reach for this on an inventory question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Balance inventory and days-on-hand

You are running `/pharmacy-operations:balance-inventory` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Measure days-on-hand — Inventory value ÷ daily COGS, by drug class.
2. Separate specialty — Specialty/refrigerated/340B handled distinctly — large tied-up cash on specialty (§3 #2 #6).
3. Read the balance — Tied-up cash vs stockout risk per class (§3 #2).
4. Set class-specific targets — Not a blanket DOH target across the book (§3 #2 #6).

## Output
A days-on-hand read by class with specialty handled distinctly and the cash/stockout balance named. See [`../skills/balance-inventory/SKILL.md`](../skills/balance-inventory/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No patient PHI in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
