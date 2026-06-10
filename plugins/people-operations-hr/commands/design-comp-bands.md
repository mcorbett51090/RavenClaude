---
description: "Design defensible comp bands tied to leveling and dated market data — set midpoints/spreads, compute compa-ratio and range penetration, surface over/under-band outliers. Reach for this on a banding or offer question."
argument-hint: "[the situation, e.g. the ladder / function / the offer in question]"
---

# Design comp bands

You are running `/people-operations-hr:design-comp-bands` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Anchor to leveling — map roles to a level ladder before any number.
2. Set band geometry — midpoint to a named, dated survey; spread; overlap (§3 #8).
3. Score the population — compa-ratio + range penetration via `scripts/people_calc.py comp-band`.
4. Surface outliers — green/red-circled and compa-ratio outliers; fix to band, not the counteroffer (§3 #2).

## Output
A band structure with midpoint/spread per level, the compa-ratio/penetration distribution, outliers flagged, and the dated survey cited. See [`../skills/design-comp-bands/SKILL.md`](../skills/design-comp-bands/SKILL.md) and [`../knowledge/people-ops-economics.md`](../knowledge/people-ops-economics.md).

## Guardrails
- Apply the §3 house opinions before any method; pay to a band, not the counteroffer.
- No named-person comp (PII) in the output; cite the survey + data-effective date (or mark it).
- End with owner / date / expected movement on each recommendation.
