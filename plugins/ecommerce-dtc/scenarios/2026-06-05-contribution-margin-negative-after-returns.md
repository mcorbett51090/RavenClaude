---
scenario_id: 2026-06-05-contribution-margin-negative-after-returns
contributed_at: 2026-06-05
plugin: ecommerce-dtc
product: returns
product_version: "n/a"
scope: likely-general
tags: [contribution-margin, returns, apparel, bracketing, reverse-logistics]
confidence: medium
reviewed: false
---

## Problem

An apparel brand's best-converting category — a fitted dress line with a great product-page conversion rate and a healthy AOV — was the one *losing money*, and the founder couldn't see it because the dashboard reported **gross** revenue and category-level conversion, not contribution margin **net of returns**. A category can convert beautifully, carry a strong AOV, and still go contribution-margin-negative once the real cost of returns (return shipping, inspection, restocking, write-off of unsellable items, and the original outbound shipping already sunk) is subtracted. Returns are a margin line, not a customer-service line (§3 #6) — and apparel is the worst case.

## Context

- Segment: apparel/fashion, ~$10M/yr, fitted-fit category with a ~35% return rate (apparel runs ~20–40%; fitted/occasion wear skews to the top of that band) [verify-at-use].
- Constraint: **bracketing** — customers ordering multiple sizes intending to keep one and return the rest — was mainstream for this category, so the return rate was structural, not a quality defect. Fit/sizing drives up to ~70% of apparel returns [verify-at-use].
- The cost stack was invisible: processing a single return runs ~20–65% of the item's original price all-in (return shipping ~$8–12, inspection ~$5–8, restocking ~$2–4, plus the sunk outbound shipping and any markdown/write-off on items that come back unsellable) [verify-at-use].

## Attempts

- Tried: rebuilt the category P&L on **net revenue per order, not gross** (§3 #2) — subtracting COGS, the blended return rate × full reverse-logistics cost, and the markdown on returned-unsellable units. Outcome: the fitted line's contribution margin went *negative* at its real return rate, while a lower-converting but low-return category was the actual profit engine.
- Tried: attacked the **return driver, not the return** — a fit problem is a merchandising/PDP fix (size guide, fit-finder, per-SKU fit notes from review text, model-measurements), not a returns-policy fix. Tightening fit guidance is the only lever that shrinks the structural rate without punishing good customers.
- Tried: modeled **whether to keep, reprice, or cut** the category — reprice up to cover the return-loaded cost, or narrow the size range to the SKUs with sane return rates, rather than killing a category that anchors the assortment. Return rate read **at the category/SKU level is an assortment signal**, not just an ops cost (see [`../best-practices/category-level-return-rate-is-the-assortment-signal-not-just-a-ops-cost.md`](../best-practices/category-level-return-rate-is-the-assortment-signal-not-just-a-ops-cost.md)).
- Tried: explicitly resisted a blanket "tighten the return policy" reflex — a stricter policy on a fit-driven category damages conversion and CLV on the *good* customers to chase a structural rate that a fit fix addresses at the source.

## Resolution

The "best" category was repriced and its size range trimmed to the SKUs with defensible return rates, and a fit-finder + review-sourced fit notes shrank the structural rate. The dashboard moved to **contribution margin net of returns** as the category scoreboard, so a high-conversion / high-return trap couldn't masquerade as a winner again. The category went from contribution-negative to thin-but-positive; the false "winner" framing was retired.

**Action for the next consultant hitting this pattern:** **never read a category on gross revenue or conversion alone — load the return cost into a per-category contribution margin** (§3 #2, #6). When the rate is fit/bracketing-driven, fix it at the PDP (size guide, fit-finder, review-sourced fit notes), not with a blanket policy that punishes good customers. The [`../scripts/dtc_calc.py`](../scripts/dtc_calc.py) `contribution-margin` mode subtracts the return-loaded cost so a category's *real* per-order margin is visible.

**Sources (retrieved 2026-06-05):**
- UpCounting — Average eCommerce return rate hit ~20% in 2025 (apparel 20–40%): https://www.upcounting.com/blog/average-ecommerce-return-rate
- Eightx — Average ecommerce return rate 2026 (~14% DTC, ~19% overall): https://eightx.co/blog/average-ecommerce-return-rate
- Richpanel — Return rates by category + the metric that matters (cost of a return, 20–65% of item price): https://www.richpanel.com/learn/ecommerce-return-rates

Return rates and per-return costs are category- and carrier-dependent — treat every figure as `[verify-at-use]` and recompute against the brand's actual reverse-logistics invoices and SKU-level return data (§3 #8).
