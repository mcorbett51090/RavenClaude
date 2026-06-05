---
scenario_id: 2026-06-05-quote-margin-erosion-surcharge-volatility
contributed_at: 2026-06-05
plugin: freight-forwarding-sales
product: quoting
product_version: "n/a"
scope: likely-general
tags: [quoting, surcharge, baf, gri, margin, validity, spot]
confidence: medium
reviewed: false
---

## Problem

A forwarder kept winning FCL quotes on a volatile Asia→Europe lane and then watching the margin evaporate between quote acceptance and booking. The seller quoted an attractive all-in, the customer sat on it for three weeks, and by booking time a mid-month **GRI** plus a **BAF** revision had moved the carrier buy rate up — but the customer held the seller to the quoted sell. Several shipments shipped at near-zero or negative margin, and the seller could not say *why* without reconstructing each quote by hand.

## Context

- Segment: mid-market BCO shipper, recurring but irregular FCL volume; lane was in a **GRI/PSS-active** window (surcharges announced ~15–30 days ahead and moving). [verify-at-use]
- Constraint: the seller quoted a single all-in number with a generous (open-ended) validity and **no subject-to-GRI/PSS clause** — so the sell was frozen while the buy floated. This is exactly the spot-vs-contract decision tree's "held spot" trap when the held window is too long.
- The seller conflated "we won the quote" with "we made the margin" — margin is realized at booking, not at acceptance, and on a volatile lane the gap between the two is where it leaks.

## Attempts

- Tried: shortened the **validity window** to match how fast the lane's surcharges move (a 30-day open quote on a lane with mid-month GRIs is a standing loss). Outcome: cut the exposure window; the buy and sell now move together.
- Tried: added an explicit **"valid until <date>; base subject to GRI/PSS/BAF in effect at booking"** line, or folded the volatile surcharges into a priced-in all-in with a buffer, per the quote-all-in-never-base-only and name-the-validity-date best-practices. Outcome: the customer either booked inside the window or re-quoted at the live rate — no more silent absorption.
- Tried: rebuilt the historical quotes with `scripts/freight_calc.py quote` to show buy/sell/margin per shipment, isolating where the surcharge delta ate the margin. Outcome: quantified the leak (it was the GRI delta, not the base rate) and made the validity-policy change defensible internally.

## Resolution

The margin was eroding not because the *base* rate was wrong but because a **long validity on a surcharge-volatile lane** froze the sell while the buy floated. The fix was commercial discipline, not a price change: a validity window matched to the lane's surcharge cadence, an explicit subject-to-GRI/PSS clause (or a priced-in buffer), and showing buy/sell/margin on every quote so erosion is visible before it ships, not after.

**Action for the next consultant hitting this pattern:** on a surcharge-volatile lane, treat **validity as a risk control, not a courtesy** — match it to how fast GRI/PSS/BAF move, and never leave a held all-in open-ended without a subject-to clause or a priced-in buffer. Reconstruct buy/sell/margin per shipment (the `quote` subcommand) before blaming the base rate; surcharge deltas, not base creep, are the usual culprit. Margin is realized at booking — quote like it.

**Sources (retrieved 2026-06-05):** ocean surcharge stack incl. GRI/PSS announced ~15–30 days ahead — https://seafreightgo.com/ocean-freight-surcharges-explained/ ; https://nyshex.com/knowledge-base/ocean-freight-surcharges-list . Specific GRI/BAF amounts and lane timing are volatile and lane-specific — treat any figure as `[example — confirm against your live rates/tariff]` and validate against the live carrier schedule (§3 #8).
