---
name: ghg-inventory
description: "Build a GHG Protocol inventory: Scopes 1/2/3 and the 15 Scope-3 categories, activity data and emission-factor sourcing with vintage, location-based vs market-based Scope 2, base-year setting and recalculation, the consolidation boundary, and data-quality tiering — every figure traceable and assurable."
---

# GHG Inventory

## Work inside the fixed boundary
Use the consolidation boundary `esg-reporting-architect` fixed (equity share / financial / operational control). The inventory boundary must match the disclosure boundary; reconcile any delta explicitly.

## Scope 1 and Scope 2
- **Scope 1** — direct combustion, fleet, fugitive, process; activity data × sourced/vintaged factor.
- **Scope 2** — report BOTH location-based (grid-average factor) AND market-based (contractual instruments: RECs/GOs, PPAs, green tariffs, supplier-specific factors) where instruments exist. Screen instruments against the Scope-2 market-based quality criteria; failures default to the grid factor. Offsets are not Scope-2 instruments and are reported separately.

## Scope 3 — screen all 15 categories
Run a relevance screen across all 15 categories (purchased goods, capital goods, fuel/energy, upstream/downstream transport, waste, business travel, commuting, leased assets, processing, use of sold products, end-of-life, franchises, investments/financed emissions). Include the material ones; document the rationale for any exclusion. Flag spend-based lines as the lower data-quality tier with a path to activity-based.

## Activity data, factors, and data quality
Every line: activity data, emission factor (source + vintage + unit), and method. A factor with no vintage is unusable — treat the line as unverified. Tier each line by data quality (primary/metered vs estimated/spend-based) so the assurer sees the weak points.

## Base year & recalculation
Set the base year deliberately; document the recalculation policy and significance threshold; recalculate on structural change (acquisition, divestiture, methodology shift) that crosses the threshold. Never net an offset into the gross inventory.

## Output
The inventory (Scope 1, dual Scope 2, Scope 3 across 15 categories), each figure with factor source/vintage and method, the Scope-3 relevance screen, the base year and recalculation policy, and data-quality tiers. Hand the evidence trail + assurance readiness to `disclosure-and-assurance-lead`.
