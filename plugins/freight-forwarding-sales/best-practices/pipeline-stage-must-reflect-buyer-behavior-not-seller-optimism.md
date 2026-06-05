# Pipeline Stage Must Reflect Buyer Behavior, Not Seller Optimism

**Status:** Absolute rule
**Domain:** Freight-forwarding sales
**Applies to:** `freight-forwarding-sales`

---

## Why this exists

A freight sales pipeline inflated with optimistic stage assignments produces a forecast that management trusts and misses. In freight forwarding, a deal that has been "at proposal stage" for 90 days with no next step and a single contact is not a pipeline deal — it is a wish. Stage definitions tied to observable, verifiable buyer behaviors (a meeting happened, a quote was requested, a trial shipment was booked) prevent wishful staging and make the weighted forecast a real planning tool rather than a CRM-cleanup exercise at quarter-end.

## How to apply

Use these behavioral stage definitions for every freight sales deal in the CRM:

```
Freight Sales Pipeline Stages — Behavioral Definitions
────────────────────────────────────────────────────────
Stage 1 — Identified
  Observable behavior:  Contact has been identified; no outreach yet or outreach sent, no response.
  Next step required:   First meeting or call booked.
  Forecast weight:      0%

Stage 2 — Discovery
  Observable behavior:  Initial meeting or call completed; shipper has described lanes/volume.
  Required evidence:    Meeting notes in CRM, volume/lane details documented.
  Next step required:   Quote request or RFQ received.
  Forecast weight:      10%

Stage 3 — Quote Delivered
  Observable behavior:  All-in quote sent and received by the decision-maker.
  Required evidence:    Quote document attached in CRM, recipient confirmed.
  Next step required:   Follow-up call scheduled within 5 business days.
  Forecast weight:      25%

Stage 4 — Active Evaluation
  Observable behavior:  Customer has asked clarifying questions, requested revisions, or
                        is comparing against at least one other forwarder.
  Required evidence:    Email thread or call notes confirming active comparison.
  Next step required:   Decision timeline confirmed with customer.
  Forecast weight:      40%

Stage 5 — Verbal / Pilot
  Observable behavior:  Customer has verbally committed or has agreed to a trial shipment.
  Required evidence:    Written or verbal confirmation in notes; trial shipment booked.
  Next step required:   SOP / rate confirmation signed.
  Forecast weight:      70%

Stage 6 — Closed Won
  Observable behavior:  First shipment booked under commercial terms.
  Forecast weight:      100%
```

**Do:**
- Require a specific "next step + date" to be logged in the CRM before any deal can advance to Stage 3 or beyond.
- Flag any deal at Stage 3 or above with no next step or no contact in 14 days as "at risk" — it is stalling, not progressing.
- Review the pipeline for deals that have been at the same stage for more than 30 days; they either need a reactivation plan or a downgrade.

**Don't:**
- Advance a deal to Stage 4 based on the seller's feeling that the customer "seems interested" — a behavioral evidence requirement must be met.
- Allow a single-threaded deal (one contact only) to be staged above Stage 3 without a plan to multi-thread.
- Use "% closed" self-estimates by the seller as the stage criterion — observable behavior, not sentiment, determines the stage.

## Edge cases / when the rule does NOT apply

Long-term strategic accounts with existing commercial relationships may have their own stage notation (renewal, expansion, at-risk-to-churn) that supplements the new-business stage definitions. Track them separately in the CRM with a clear account-type label.

## See also

- [`../agents/pipeline-forecast-coach.md`](../agents/pipeline-forecast-coach.md) — owns pipeline hygiene, stage enforcement, and forecast methodology.
- [`../agents/key-account-manager.md`](../agents/key-account-manager.md) — applies account-specific stage logic for existing customer expansions.

## Provenance

Codifies CLAUDE.md §3 #5 (the CRM is the forecast — a deal with no next step, owner, and date isn't real) and the anti-pattern "pipeline stuffed with alive deals that have no next step." Behavioral stage definitions are a standard B2B sales hygiene practice; the freight-forwarding-specific stage criteria reflect the typical 6–18 month logistics-sales cycle [unverified — training knowledge].

---

_Last reviewed: 2026-06-05 by `claude`_
