---
scenario_id: 2026-06-08-scope-3-cherry-picked-categories
contributed_at: 2026-06-08
plugin: esg-sustainability-reporting
product: ghg-protocol
product_version: "unknown"
scope: likely-general
tags: [scope-3, materiality, financed-emissions, boundary, assurance]
confidence: high
reviewed: false
---

## Problem

A consumer-products company published a Scope 3 footprint covering six of the 15 categories — business travel, employee commuting, waste, and a few easy upstream ones — and headlined a year-on-year Scope 3 reduction. The largest plausible category for their business, category 11 (use of sold products), wasn't in the inventory at all, and category 1 (purchased goods & services) was estimated only for a handful of named suppliers. There was no documented screen explaining why the other nine categories were absent. When the assurance provider reviewed the boundary, the "reduction" collapsed: the reported total had fallen mainly because a category that had been partially estimated the prior year was dropped entirely this year.

## Constraints context

- First year attempting a Scope 3 number beyond the trivial categories.
- A products business where downstream use-phase emissions were almost certainly dominant.
- A reduction narrative already in the draft annual report.

## Attempts

- Tried: keep the six-category inventory and add a sentence that Scope 3 was "partial." Rejected — a partial Scope 3 with no screen of all 15 and no rationale for the omissions isn't assurable, and dropping a category year-on-year broke the trend claim outright.
- Tried: run a proper relevance screen across all 15 categories using spend-based and proxy data first, dispositioning each as not-relevant / screened-out-with-threshold / included. This surfaced that categories 1 and 11 were material and had to be in.
- Tried: estimate categories 1 and 11 with a documented method and a data-quality flag (spend-based for 1, a use-phase model for 11), included with an improvement plan rather than dropped. This restored a defensible boundary.

## Resolution

The inventory moved to a documented 15-category screen: each category dispositioned, the material ones (notably 1 and 11) included with their method and data-quality tier, and the excluded ones recorded with the threshold and proxy used. The reduction headline was withdrawn because the prior-year comparison wasn't on a like-for-like boundary; a restated baseline on the full screen replaced it. The assurer could then trace the boundary itself, not just the totals inside it.

## Lesson

Screen all 15 Scope-3 categories — exclusion is a documented decision, not a default. Cherry-picking the easy categories and dropping the hard ones (use of sold products, purchased goods & services, financed emissions) shrinks the denominator and manufactures a "reduction" that won't survive assurance. Screen everything, include the material, document every omission.
