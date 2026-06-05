---
scenario_id: 2026-06-05-single-source-supply-risk-dual-source
contributed_at: 2026-06-05
plugin: procurement-sourcing
product: supply-risk
product_version: "n/a"
scope: likely-general
tags: [single-source, supply-risk, dual-source, continuity, bottleneck]
confidence: medium
reviewed: false
---

## Problem

A low-spend component — barely a rounding error in the spend cube — was single-sourced from one supplier, and a near-miss (a multi-week allocation during a market shortage) had nearly taken a production line down. Leadership's instinct was to "negotiate a better price" with the supplier. That was the wrong frame: this was a **continuity** problem, not a price problem, and the category was being mis-played because it had been mis-placed on the Kraljic matrix.

## Context

- Segment: direct material, manufacturer, the item was spec-locked (engineering-qualified to one supplier's part) — switching meant a re-qualification cycle measured in months.
- Constraint: low annual spend made it invisible to a spend-threshold-driven sourcing pipeline, so it had never been segmented — nobody had placed it on the matrix.
- The team conflated "small spend" with "low importance." On Kraljic this is the **bottleneck** quadrant (low profit impact, high supply risk) — the failure mode is exactly treating it like a non-critical/leverage item and chasing price.

## Attempts

- Tried: re-placed the category using the Kraljic-positioning tree (`knowledge/procurement-kraljic-positioning-decision-tree.md`) — low profit impact, high supply risk → **bottleneck**, whose play is *secure continuity*, explicitly not cost reduction. Outcome: reframed the whole engagement from "negotiate price" to "de-risk supply."
- Tried: scoped the de-risking options in cost order — (1) qualify a **second source** (dual-source), (2) negotiate a continuity/priority-of-supply clause + safety stock with the incumbent as the interim bridge, (3) a longer-term agreement to earn allocation priority. Began second-source qualification immediately rather than waiting for the next disruption (the supplier-distress tree's "qualify now if lead time allows" branch). Outcome: a backup supplier in qualification + an interim safety-stock buffer.
- Tried: priced the **switching/qualification cost** honestly as part of the TCO so the dual-source business case wasn't undercut by "but it's cheaper to stay single." Outcome: the continuity premium was framed as insurance against a line-down, not as a cost overrun.

## Resolution

The right move was **dual-source + a continuity clause + interim safety stock**, not a price negotiation. The category was a textbook bottleneck item mis-played as non-critical because its spend was small; correct Kraljic placement flipped the strategy. The continuity premium (qualification cost + carry on safety stock) was cheap relative to a line-down.

**Action for the next consultant hitting this pattern:** small spend ≠ low importance. **Place the category on the Kraljic matrix before choosing a play** (§3 #1) — a low-spend, hard-to-switch, single-source item is a *bottleneck*, and the play is securing continuity (dual-qualify, safety stock, priority clauses), NOT price. Begin alternate-supplier qualification *before* the next disruption if any lead time exists — don't wait for failure. Price switching/qualification cost into the TCO so the dual-source case stands (§3 #2).

**Sources (retrieved 2026-06-05):** Kraljic bottleneck-quadrant play (secure supply, low spend / high risk) — https://www.cips.org/intelligence-hub/supplier-relationship-management/kraljic-matrix ; https://artofprocurement.com/blog/learn-the-kraljic-matrix . Switching cost as a TCO component — https://www.cips.org/intelligence-hub/finance/total-cost-of-ownership . No client-specific figures appear here; any quantification is `[ESTIMATE]` pending the client's actual lead-time and spend data (§3 #8).
