---
scenario_id: 2026-06-05-renewal-retention-leak
contributed_at: 2026-06-05
plugin: insurance-pc
product: agency-distribution
product_version: "n/a"
scope: likely-general
tags: [retention, renewal, persistency, agency, new-business-loss-ratio]
confidence: medium
reviewed: false
---

## Problem

An agency-distributed personal-lines book was growing premium but the underwriting result was drifting worse. Leadership wanted to "write more new business to grow out of it." The risk: new business retains worse and runs a worse loss ratio than seasoned renewals, so leaning harder on new business while a retention leak goes unaddressed both raises acquisition cost AND worsens the loss ratio — growing into a loss.

## Context

- Segment: independent-agency-distributed personal lines (auto + home), competitive rate environment.
- Constraint: retention is the cheapest premium there is — re-acquiring a lost policyholder costs far more than keeping one, and a first-year book is more price-sensitive and runs a higher loss ratio than a multi-year book (the new-business penalty). Public benchmarks for scale: the standard P&C agency retention average is ~88%, bundled auto+home retain ~91% vs ~67% for monoline, and moving retention from 88% to 94% yields ~16% more policies after 5 years [verify-at-use].
- The team was treating new-business volume as the growth lever while a renewal leak quietly drained the seasoned, profitable book.

## Attempts

- Tried: **measured retention / persistency by tenure and by bundling** before adding new business. Outcome: monoline policies were churning hard (price-shoppers), while bundled multi-year accounts were sticky — the leak was concentrated, not uniform. Retention drivers from the literature: only ~13% of clients shop on a rate increase, but ~28% start shopping over poor service, and clients who speak to their agent before renewal are far likelier to stay [verify-at-use].
- Tried: **compared the new-business loss ratio to the renewal loss ratio** (the new-business penalty) before treating new business as the fix. Outcome: new business ran materially worse — so "write more new business" would have worsened the blended loss ratio while raising acquisition cost, the opposite of the intended fix.
- Tried: **a retention-first plan** — pre-renewal agent contact, bundling/cross-sell on monoline accounts, and a service-quality fix — sized against the cheaper-than-acquisition economics. Outcome: plugged the leak on the profitable seasoned book, improving the blended result without buying a worse-loss-ratio new-business cohort.

## Resolution

The action plan led with **retention** (pre-renewal contact, bundling the monoline churners, fixing the service driver) and treated new business as the *second* lever, priced to adequacy — not as the growth shortcut. The deliverable separated retention by tenure and bundling, and the new-business vs renewal loss ratio, so the cheaper, better-loss-ratio premium (renewals) was protected first.

**Action for the next consultant hitting this pattern:** **fix the retention leak before leaning on new business.** Retained premium is cheaper and runs a better loss ratio than new business; growing through new business while a renewal leak runs open raises acquisition cost AND the loss ratio. Measure retention by tenure and bundling, compare the new-business vs renewal loss ratio, and act on the concrete drivers (pre-renewal contact, bundling, service) — most churn is service-driven, not rate-driven. Then price new business to the loss ratio, not the competitor (§3 #2). Pair with the rate-adequacy discipline; the [`../scripts/pc_calc.py`](../scripts/pc_calc.py) `rate-indication` mode checks whether the new-business rate is adequate before you grow it.

**Sources (retrieved 2026-06-05):**
- Agency Performance Partners — insurance policy retention (88% average; monoline vs bundled; shopping drivers): https://www.agencyperformancepartners.com/blog/insurance-policy-retention/
- WaterStreet — renewal retention analytics for P&C: https://www.waterstreetcompany.com/renewal-retention-analytics/
- Bain & Company — improving customer retention in P&C insurance: https://www.bain.com/insights/how-to-improve-customer-retention-in-property-and-casualty-insurance-snap-chart/

Retention percentages and shopping-driver figures are agency-survey benchmarks, not hard rules — treat as `[verify-at-use]` and validate against the book's own persistency and loss-ratio-by-tenure data (§3 #8).
