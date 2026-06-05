# Warranty Call Tracking Is a Quality and Cost Control System

**Status:** Pattern
**Domain:** Field operations / quality management
**Applies to:** `skilled-trades-contracting`

---

## Why this exists

Warranty callbacks — return trips to fix work that didn't hold — are the most expensive calls a service business handles. The labor is free to the customer and costs the contractor full loaded rate plus truck time plus opportunity cost (a truck on a warranty call is not billing). Contractors who don't track warranty calls separately from billable service calls cannot measure their true warranty cost, cannot identify recurring failure modes by technician or part, and cannot make the training or parts-sourcing decisions that reduce the rate. A 5% warranty call rate on a technician averaging $400 per first-call job is $20 in warranty cost per $400 of revenue — 5% direct margin erosion before any other cost.

## How to apply

Build the warranty tracking system into the dispatch and job-cost flow:

```
Warranty call tracking (per call):
  Job ID of original work:       ______
  Original technician:           ______
  Original work date:            ______
  Warranty call date:            ______
  Days since original work:      ______
  Warranty call technician:      ______
  Labor hours on warranty call:  ______   × loaded rate = $______
  Parts used (warranty or billable): $______
  Root cause determined:         ______

  Classification:
    [ ] Technician error (wrong diagnosis, missed step)
    [ ] Parts failure (defective component, wrong part selected)
    [ ] Scope error (problem was outside original repair — not a warranty)
    [ ] Customer use / external factor — document and close without rework

Monthly warranty dashboard:
  Total warranty calls:           ______
  As % of total service calls:    ______%  (target: < 3% [unverified])
  Total warranty labor cost:      $______
  Warranty calls by technician:   (rank — flag outliers at 2x average rate)
  Warranty calls by part/system:  (identify failure-mode concentrations)
```

**Do:**
- Require root-cause documentation on every warranty call — without it, the data is a count, not a diagnostic tool.
- Review warranty rates by technician monthly; a technician at 2x the team average needs coaching or a skills audit, not just an observation.
- Escalate recurring part failures to the supplier or manufacturer; a part that fails at 3x normal rate is either defective or being installed outside its design parameters.

**Don't:**
- Classify a callback as a "goodwill visit" rather than a warranty call to protect a technician's record — the cost is real whether it is classified accurately or not.
- Ignore warranty calls that happen just outside the warranty window; they are quality signals even when they are billable.

## Edge cases / when the rule does NOT apply

New-construction defect calls follow a different classification (punch-list vs. warranty vs. owner-caused) governed by the construction contract; the tracking discipline applies, but the category structure is different. Sub-contractor-performed work that triggers a warranty call should be tracked separately and charged back to the sub per the subcontract terms.

## See also

- [`../agents/field-operations-specialist.md`](../agents/field-operations-specialist.md) — owns the warranty call root-cause analysis and technician coaching.
- [`../agents/trade-business-analyst.md`](../agents/trade-business-analyst.md) — owns the warranty cost calculation and its inclusion in the job-cost and P&L analysis.
- [`./first-time-fix-and-callback-rate-are-margin-not-just-quality.md`](./first-time-fix-and-callback-rate-are-margin-not-just-quality.md) — warranty tracking is the upstream diagnostic that feeds first-time-fix improvement; the two rules are the same problem viewed from different directions.

## Provenance

Warranty call tracking and root-cause analysis are standard in HVAC and service contractor quality management; callback-rate benchmarking is covered in Nexstar Network and ACCA contractor operations resources.

---

_Last reviewed: 2026-06-05 by `claude`_
