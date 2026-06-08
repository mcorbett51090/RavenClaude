---
name: design-comp-bands
description: "Design defensible comp bands tied to leveling and dated market data — set midpoints/spreads, compute compa-ratio and range penetration, surface over/under-band outliers. Reach for this on a banding or offer question."
---

# Skill: Design comp bands

Pay to a band, not the counteroffer (§3 #2); a band is only as defensible as its dated survey (§3 #8).

## Step 1 — Anchor to leveling
Map roles to a level ladder before any number; comp follows level, not tenure or negotiation.

## Step 2 — Set band geometry
Midpoint to market (named survey + data-effective date), spread (min–max), and overlap between adjacent bands.

## Step 3 — Score the population
Compa-ratio (salary ÷ midpoint) and range penetration per person. Use [`../../scripts/people_calc.py`](../../scripts/people_calc.py) `comp-band`.

## Step 4 — Surface outliers
Green-circled (over band — freeze, don't compound), red-circled (under band — fix to band, not ad hoc), and compa-ratio outliers (§3 #2).

## Output
A band structure with midpoint/spread per level, the compa-ratio/penetration distribution, the outliers flagged, and the dated survey cited. See [`../../knowledge/people-ops-economics.md`](../../knowledge/people-ops-economics.md) §3.
