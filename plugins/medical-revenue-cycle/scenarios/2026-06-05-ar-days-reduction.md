---
scenario_id: 2026-06-05-ar-days-reduction
contributed_at: 2026-06-05
plugin: medical-revenue-cycle
product: accounts-receivable
product_version: "n/a"
scope: likely-general
tags: [accounts-receivable, ar-days, aging, timely-filing, worklist]
confidence: medium
reviewed: false
---

## Problem

A specialty practice's days-in-A/R had drifted past 50 and the CFO read it as "collections is slow." The single blended A/R-days number was masking the real shape of the problem: the average looked bad, but the average is a denominator artifact — it hides where the cash is actually stuck. The team was working the A/R by patient alphabetically, which is functionally random with respect to recoverable dollars.

## Context

- Segment: single-specialty physician-group, commercial-heavy payer mix.
- Constraint: a credentialing gap on two newer providers meant a slice of claims literally could not be paid (no payable provider record) and was aging in the >90 bucket — invisible in the blended number.
- The CFO conflated "A/R days is high" (the headline) with "collectors are slow" (one cause). Reading A/R as a single average instead of by **aging bucket and payer** is the misread §3 #3 exists to prevent.

## Attempts

- Tried: **segmented A/R by aging bucket and by payer** before touching the work queue (§3 #3). The over-90-day bucket was well above the <10% target and was concentrated in (a) the two un-credentialed providers' claims and (b) one slow commercial payer. Outcome: reframed from "collect faster" to "fix the credentialing block + work the concentrated buckets."
- Tried: re-prioritized the work-down — **timely-filing-risk claims first** (a missed filing deadline, CARC CO-29, is a 100% permanent loss), then **recoverable-dollar-weighted** within bucket, deprioritizing tiny balances and known-uncollectible (§3 #3). Outcome: stopped the silent timely-filing leakage; recovered the aged commercial bucket.
- Tried: escalated the **provider-credentialing gap** as its own track (front-end revenue protection — a claim from an un-credentialed provider cannot be paid no matter how well it is worked). Outcome: once the providers were enrolled, that slice of >90 A/R cleared and stopped regenerating.

## Resolution

High A/R days was **not** a collector-speed problem — it was a concentration problem (credentialing block + one slow payer) hidden by a blended average. The fix: read A/R by bucket-and-payer, work it by deadline-then-dollars, and treat credentialing as front-end revenue protection rather than an HR afterthought. Days-in-A/R moved back toward the high-performer range (under ~40) [ESTIMATE — validate against the client's aging report].

**Action for the next consultant hitting this pattern:** **never act on a blended A/R-days number** — segment by aging bucket and payer first (§3 #3); the over-90 bucket (target <10% of total A/R) usually concentrates in a couple of fixable causes. Sequence the work-down **timely-filing-risk first, then recoverable-dollar-weighted**, not alphabetically or FIFO. Check for a **credentialing block** early — un-credentialed-provider claims age in >90 and can't be worked to payment until enrollment closes. The [`../scripts/rcm_calc.py`](../scripts/rcm_calc.py) `ar-days` mode computes days-in-A/R from outstanding A/R and average daily charges.

**Sources (retrieved 2026-06-05):** days-in-A/R + >90-day targets — https://www.mdclarity.com/blog/rcm-benchmarks and https://www.hfma.org/revenue-cycle/kpis/7-kpis-providers-should-be-tracking/ ; A/R aging blind spots — https://www.medicalbillersandcoders.com/blog/ar-aging-gaps-your-dashboard-hides/ ; timely-filing (CARC CO-29) — https://www.sprypt.com/denial-codes/carc-and-rarc-codes . Specific bucket percentages are practice-dependent; treat any number here as `[ESTIMATE]` and build from the client's aging report (§3 #8).
