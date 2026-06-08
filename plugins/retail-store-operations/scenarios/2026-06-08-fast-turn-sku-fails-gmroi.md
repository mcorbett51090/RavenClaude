---
scenario_id: 2026-06-08-fast-turn-sku-fails-gmroi
contributed_at: 2026-06-08
plugin: retail-store-operations
product: merchandising
product_version: "unknown"
scope: likely-general
tags: [gmroi, space-productivity, assortment, margin, turns]
confidence: high
reviewed: false
---

## Problem

A category buyer defended a hero SKU and kept expanding its facings because "it flies off the shelf" — it had the fastest turn in the category. But the category's overall margin kept eroding as the SKU grew. On a closer read, the SKU turned fast but at a thin margin, and the extra facings were borrowed from slower-turning but far higher-margin items. The shelf was optimizing for turn and quietly losing margin dollars and capital efficiency.

## Constraints context

- The only metric on the category review was inventory turns; GMROI and margin-per-facing weren't shown.
- Facings were allocated by turn and by vendor pressure, not by space productivity (sales and margin per facing).
- "Fast turn = good inventory" was the unexamined assumption driving the facing expansion.

## Attempts

- Tried: expanding the fast-turner's facings on the strength of its turn rate. Eroded category margin — the SKU's GMROI was actually below the rest of the category because its margin was thin, so each added facing diluted the category's capital efficiency.
- Tried: reading GMROI (gross margin $ / average inventory cost at the same window) alongside turn. This exposed it — the fast-turner cleared the flow test but failed the capital test, while the items it was crowding out earned far more per facing.
- Tried: re-allocating facings by space productivity and role — keeping enough of the traffic-driving fast-turner to own its decision, but giving facings back to the higher-GMROI margin-drivers. Category margin dollars and blended GMROI recovered without losing the traffic SKU.

## Resolution

The category review added GMROI and margin-per-facing next to turn, and facings were re-allocated by space productivity and role (traffic-driver vs. margin-driver) rather than by raw turn or vendor pressure. The fast-turner kept enough space to do its traffic job but stopped crowding out the items that actually earned the capital. The shelf went back to earning, not just turning.

## Lesson

GMROI is the capital lens; turn alone doesn't prove earning. Fast-turning, low-margin inventory can turn beautifully and still fail the GMROI test, and shelf space is finite capital — allocate facings by space productivity and role, not by turn rate or vendor pressure. Read the flow lens and the capital lens together before defending a facing.
