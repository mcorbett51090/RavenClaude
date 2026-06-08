---
scenario_id: 2026-06-08-occupancy-win-revpar-loss
contributed_at: 2026-06-08
plugin: hospitality-hotel-operations
product: ideas
product_version: "unknown"
scope: likely-general
tags: [revpar, adr, occupancy, channel-mix, net-adr, ota, goppar]
confidence: high
reviewed: false
---

## Problem

A 140-room independent hotel was celebrating a record quarter: occupancy was up to 92% and management was thrilled. But the GM noticed the bank balance wasn't reflecting the "record" — RevPAR was actually *down* year-over-year and GOPPAR had fallen harder. The front office had been told to "fill the house," so they leaned on deep OTA discounts and last-minute giveaways to hit occupancy, and reported success on the one number they were measured on.

## Constraints context

- Heavy reliance on Booking.com and Expedia, commissions ~18-22%, with the team comparing channels on *headline* rate only.
- The property was measured and bonused on occupancy, so every incentive pushed toward filling rooms at any rate.
- No demand forecast — the team reacted to the booking pace, discounting whenever pickup looked soft a few days out.

## Attempts

- Tried: pushing occupancy even higher with broader discounts. Failed — RevPAR fell further; each discounted room added occupancy but subtracted average rate faster, and the high-commission channels ate the thin remaining margin.
- Tried: a blanket "raise rates 10%" mandate. Failed — it choked pickup on genuinely soft dates and left high-demand dates still underpriced, because it wasn't tied to a demand view.
- Tried: re-anchoring on RevPAR read against GOPPAR, building a by-date demand forecast, and comparing channels on **net ADR** (rate minus commission). Held rate into forecasted strong demand, used fenced LOS/advance-purchase discounts only into soft dates where the lower rate still raised RevPAR, and shifted marginal volume from 20%-commission OTA to a direct value prop. This worked.

## Resolution

Switching the scorecard from occupancy to RevPAR (with GOPPAR as the profit check) immediately changed behavior. Occupancy settled to ~85% but ADR rose enough that RevPAR climbed double digits and GOPPAR recovered, because the discounting stopped being reflexive and the net-ADR view killed the worst OTA giveaways. The demand forecast turned pricing from reactive to positioned — rate held where demand was strong, fenced discounts only where they actually lifted RevPAR.

## Lesson

RevPAR is the north-star, not occupancy — a 92% house can be a worse business than an 85% one. Read RevPAR against GOPPAR so you don't buy occupancy with unprofitable cost, compare every channel on net ADR after commission, and forecast demand so pricing positions ahead of the booking pace instead of reacting to it.
