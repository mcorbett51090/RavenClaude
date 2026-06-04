---
description: "Build acuity-based pricing that captures the care cost by level, instead of a flat rate, to protect margin. Reach for this on a pricing question."
argument-hint: "[the situation, e.g. the metric/segment in question]"
---

# Price to acuity

You are running `/senior-care-operations:price-to-acuity` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Define acuity levels — Care-need tiers and the hours each implies (§3 #2).
2. Cost the care by level — The labor and service cost per acuity tier (§3 #3).
3. Set level-based rates — Price each level to cost plus margin.
4. Find the under-priced — Surface where current flat pricing loses money.

## Output
An acuity-level definition, the care cost by level, level-based rates, and the under-priced gap. See [`../skills/price-to-acuity/SKILL.md`](../skills/price-to-acuity/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method.
- No client PII; cite or mark every external figure.
