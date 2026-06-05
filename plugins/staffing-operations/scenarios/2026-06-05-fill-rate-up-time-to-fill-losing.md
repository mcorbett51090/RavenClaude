---
scenario_id: 2026-06-05-fill-rate-up-time-to-fill-losing
contributed_at: 2026-06-05
plugin: staffing-operations
product: operations-analytics
product_version: "n/a"
scope: likely-general
tags: [fill-rate, time-to-fill, speed, order-quality, submittal]
confidence: medium
reviewed: false
---

## Problem

An allied-health division reported a **healthy fill rate (~78% on workable orders, trailing 90 days)** but was quietly losing repeat orders from two anchor MSP accounts. The VP of Operations read the fill rate as "we're fine on these accounts" and wanted to redirect attention to a lower-filling division. The real disease was invisible in the fill-rate number: the division filled well but **slowly**, and the fast competitor on the same MSP req pool was taking the placements before our qualified submittal landed.

## Context

- Segment: healthcare-allied, MSP/VMS-fed, dual-vendor on the affected accounts.
- Constraint: fill rate alone was being used as the account-health metric — the classic single-number trap (CLAUDE.md §3 #2). Time-to-fill was tracked but reported on a *separate* slide, so no one read the pair together.
- The MSP scorecard rewards **time-to-present**, not just fill; a vendor that presents in <48h gets first look at the next req. Our time-to-present had slipped to ~36h average with a long right tail.

## Attempts

- Tried: **paired fill rate with time-to-fill on the same tile** (§3 #2) and re-cut time-to-fill *to start* (post-credentialing), not to offer-accept (§3 #7). Outcome: the "healthy" division's time-to-fill-to-start was ~38 days vs. a competitive ~30, and time-to-submit had a long tail — the speed problem the fill number masked.
- Tried: **split supply vs. order-quality** (§3 #6) to be sure this wasn't a thin-pipeline problem in disguise. Submittals-per-workable-order were fine and bill rates were at-market, so it was a **latency** problem, not supply or pricing — which means adding candidates would NOT have helped.
- Tried: walked the funnel stage-by-stage to localize the latency — order-to-workable and workable-to-submittal were on pace; the drag was in **time-to-submit** (intake-to-first-qualified-presentation) and a credentialing tail at accept→start. Outcome: pinpointed the two stages to fix rather than "go faster everywhere."

## Resolution

The finding flipped from "this division is healthy" to "this division is **losing on speed despite good fill**" — a different disease with the opposite fix (latency reduction, not more sourcing). The recommendation targeted time-to-submit (intake SLA + pre-qualified bench for the recurring req shapes) and the credentialing tail, with fill rate held as a guardrail so a speed push didn't quietly drop quality.

**Action for the next consultant hitting this pattern:** **never read fill rate without time-to-fill in the same breath** (§3 #2) — a high-fill / slow-speed division is losing placements to faster competitors, and the fix (cut latency) is the opposite of the low-fill fix (add supply). Measure time-to-fill *to start* (§3 #7) so the credentialing tail isn't hidden, and localize the latency to a specific funnel stage before prescribing. See [`../knowledge/staffing-decision-trees.md`](../knowledge/staffing-decision-trees.md) "Fill rate has declined" (step 4 pairs the two) and [`../best-practices/pair-fill-rate-with-time-to-fill.md`](../best-practices/pair-fill-rate-with-time-to-fill.md). The [`../scripts/staffing_calc.py`](../scripts/staffing_calc.py) `funnel-leak` mode localizes the worst-converting stage from your stage rates.

**Sources (retrieved 2026-06-05):**
- Submittal-to-hire and submittal-to-interview benchmark ranges: https://recruiterflow.com/blog/recruiting-metrics/
- Fill-rate denominators + time-to-fill pairing (plugin canonical): [`../knowledge/staffing-kpi-glossary.md`](../knowledge/staffing-kpi-glossary.md) §A.1–A.2

Benchmark ranges are advisory-blog `[ESTIMATE]`, directional only — calibrate to the client's own MSP scorecard and division baseline before any deliverable (§3 #1, §3 #9). The "fast submittal wins the placement" dynamic is practitioner consensus, not an audited statistic — treat as `[verify-at-use]`.
