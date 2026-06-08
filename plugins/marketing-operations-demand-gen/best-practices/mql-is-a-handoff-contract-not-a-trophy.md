# MQL is a handoff contract, not a trophy

**Status:** Absolute rule
**Domain:** Demand generation / marketing operations
**Applies to:** `marketing-operations-demand-gen`

---

## Why this exists

Marketing Qualified Lead (MQL) volume is the single most commonly gamed metric in B2B marketing.
When Marketing unilaterally sets a low MQL threshold to hit its quota, Sales receives low-quality
leads it ignores, Marketing claims success, and the two teams distrust each other. The result is a
broken funnel where MQL volume is meaningless noise and Sales builds its own lead sources to
circumvent marketing entirely.

The MQL has value only when it is a **bilateral contract**: Marketing and Sales agree on the
definition, the score threshold, the speed-to-lead SLA, the rejection taxonomy, and the feedback
loop. A MQL that sits unworked for days is a broken SLA — not a marketing win.

## How to apply

- **Set the MQL threshold jointly** — Marketing and Sales (plus RevOps) must co-own the definition.
  The score threshold, the fit criteria, and the bypass rules are negotiated, not declared.
- **Establish a speed-to-lead SLA** — define the expected follow-up window (e.g., ≤5 business hours
  for inbound MQLs [verify-at-use]) and enforce it via automation routing and SLA alerts.
- **Build a rejection taxonomy** — when Sales rejects an MQL, they classify it: bad timing, bad fit,
  already a customer, no budget, already in Sales cycle. This taxonomy is the feedback loop.
- **Run a quarterly scoring committee** — review rejection reasons, adjust thresholds, recalibrate
  fit criteria. Marketing and Sales own this meeting together.

**Do:**

- Measure MQL→SQL conversion rate alongside MQL volume. Volume without conversion is a lagging
  indicator of a broken definition.
- Report rejection reasons to Marketing leadership — they are product feedback on the scoring model.
- Align MQL targets to pipeline targets, not to headcount or campaign budget.

**Don't:**

- Set MQL thresholds unilaterally to hit a Marketing OKR.
- Report MQL volume as a marketing success without disclosing the SQL conversion rate.
- Ignore Sales rejection reasons — they are the most honest signal Marketing receives.
- Create "bypass rules" (e.g., all event leads are MQLs) without Sales buy-in.

## Edge cases / when the rule does NOT apply

A genuine emergency — a product outage that generates an unusual inbound spike, an event that floods
the queue — may require a temporary threshold adjustment. This is the exception, not an escape hatch.
Document it, time-bound it, and revert when the event is over.

## See also

- [`./lead-scores-decay-maintain-them.md`](./lead-scores-decay-maintain-them.md)
- [`../skills/lead-scoring-and-lifecycle/SKILL.md`](../skills/lead-scoring-and-lifecycle/SKILL.md)

## Provenance

Codifies the SiriusDecisions (now Forrester B2B Research) Demand Waterfall principle that MQL is a
**bilateral** stage-gate between Marketing and Sales, and the practitioner consensus documented in
MO Pros community research and Demand Gen Report that MQL-volume-only metrics are the leading cause
of Marketing/Sales distrust.

---

_Last reviewed: 2026-06-08 by `claude`._
