---
description: "Build a GHG Protocol inventory: Scope 1/2/3 with sourced/vintaged factors, a 15-category Scope-3 relevance screen, dual location- and market-based Scope 2, the base year and recalculation policy, and data-quality tiers."
argument-hint: "[fixed boundary + available activity data (energy, fleet, supply chain, travel)]"
---

You are running `/esg-sustainability-reporting:build-ghg-inventory`. Use `ghg-accounting-analyst` + the `ghg-inventory` skill.

## Steps
1. Confirm the consolidation boundary `esg-reporting-architect` fixed; reconcile any delta to the disclosure boundary. If unfixed, route back to scope first.
2. Calculate Scope 1 (combustion/fleet/fugitive/process) and Scope 2 — report BOTH location-based and market-based where instruments exist; screen instruments against the Scope-2 market-based criteria; name them.
3. Screen all 15 Scope-3 categories for relevance; include the material ones; document the rationale for any exclusion. Flag spend-based lines as the lower data-quality tier.
4. For every line, record activity data, emission factor (source + vintage + unit), and method. A factor with no vintage → treat the line as unverified. Never net an offset into the gross inventory.
5. Set/confirm the base year, the recalculation policy, and the significance threshold; recalculate if structural change crosses it.
6. Emit the GHG-inventory-report template + the Structured Output block (with `Framework & clause:` and `Assurance posture:`). Hand the evidence trail to `disclosure-and-assurance-lead`.
