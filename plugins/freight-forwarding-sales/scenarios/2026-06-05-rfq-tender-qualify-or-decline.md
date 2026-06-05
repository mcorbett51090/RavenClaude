---
scenario_id: 2026-06-05-rfq-tender-qualify-or-decline
contributed_at: 2026-06-05
plugin: freight-forwarding-sales
product: rfq-tender
product_version: "n/a"
scope: likely-general
tags: [rfq, tender, qualify, win-rate, bid-no-bid, capacity]
confidence: medium
reviewed: false
---

## Problem

A small forwarder's sales team was "busy losing" — chasing every RFQ that hit the inbox, pricing nights and weekends, and winning a dismal share. The pricing desk was the bottleneck: by the time a 40-lane ocean+air matrix with local charges was assembled, the deadline was hours away and the bid went out rushed or late. The owner read low win rate as a *pricing* problem ("we're too expensive") when it was really a **qualification** problem — too many doomed bids drowning the winnable ones.

## Context

- Segment: independent forwarder, manual quoting, no bid/no-bid gate; every RFQ was treated as equally worth pursuing.
- Constraint: a real operational driver of quote win rate is **response speed + accuracy + carrier optionality + margin consistency** — and a desk buried in un-winnable bids is slow and inconsistent on the ones it could win. Slow, surcharge-incomplete bids lose structurally, independent of price. [verify-at-use]
- The team conflated "more bids submitted" with "more pipeline," ignoring that pricing hours are the scarce resource and that a polite, fast decline on a poor-fit tender returns the week to winnable work (the quote-vs-qualify decision tree's whole point).

## Attempts

- Tried: installed a **qualify-or-decline scorecard before pricing** — strategic fit (our lanes/modes), real-and-material volume (not a price-check), a relationship/known-criteria path, winnable-at-acceptable-margin, and deliverability — and declined fast on any tender that failed it, per the rfq-qualification-scorecard and tender-deadlines best-practices. Outcome: the pricing desk's load dropped sharply; the remaining bids got faster, more complete, more consistent.
- Tried: on RFIs / very-early intel-only requests, **responded lean** to shortlist and learn criteria rather than building a full matrix. Outcome: stayed in the running on early-stage tenders without sinking pricing hours.
- Tried: reframed the metric from *bids submitted* to *win rate on qualified bids* and tracked decline reasons, so "we declined 6 poor-fit tenders" read as a win, not a gap. Outcome: declining well became a tracked discipline, not a failure.

## Resolution

Low win rate was a **qualification** failure, not a pricing one. Gating every RFQ through a bid/no-bid scorecard, declining poor-fit tenders fast, and responding lean to RFIs concentrated the scarce pricing hours on winnable, deliverable business — which raised both speed and win rate on the bids that mattered. The lesson the team had inverted: *fewer, better-qualified bids beat more bids*.

**Action for the next consultant hitting this pattern:** when win rate is low and the desk is buried, **look at qualification before price** — count how many bids never had fit, real volume, a criteria path, or winnable margin. Gate with a scorecard, decline poor-fit tenders fast (a reasoned decline preserves the relationship and the next invite), and respond lean to RFIs. Track *win rate on qualified bids* and *decline reasons*, not raw bid count. Speed, surcharge-accuracy, optionality, and margin consistency are the operational win-rate drivers — protect them by not drowning the desk.

**Sources (retrieved 2026-06-05):** operational factors driving quote win rate (response speed, all-in accuracy, carrier optionality, margin consistency) — https://www.cargorates.ai/blog/how-freight-forwarders-win-more-quotes-operational-factors-drive-quote-win-rate ; slow/unstructured tender responses lose — https://www.datamondial.com/en/losing-logistics-tenders-unstructured-data-rfq-speed/ . Public industry-wide qualification-rate / no-bid-ratio benchmarks are not reliably published — any specific win-rate figure is `[unverified]`; calibrate to your own funnel (§3 #8).
