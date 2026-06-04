---
description: "Run a sourcing decision on TCO — freight, quality, switching, inventory, lifecycle — not unit price, so a price 'savings' doesn't raise total cost. Reach for this on any sourcing event."
argument-hint: "[the situation, e.g. the metric/segment in question]"
---

# Source on total cost of ownership

You are running `/procurement-sourcing:source-on-total-cost-of-ownership` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Build the TCO model — Unit price plus freight, quality, switching, inventory, lifecycle (§3 #2).
2. Compare bids on TCO — Rank suppliers on total cost, not headline price.
3. Stress the assumptions — Test the non-price drivers that swing TCO.
4. Recommend on total cost — Choose the lowest defensible TCO, not lowest price.

## Output
A TCO model, a TCO-ranked bid comparison, and a total-cost recommendation. See [`../skills/source-on-tco/SKILL.md`](../skills/source-on-tco/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method.
- No client PII; cite or mark every external figure.
