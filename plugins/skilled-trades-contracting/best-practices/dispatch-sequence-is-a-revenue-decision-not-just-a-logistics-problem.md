# Dispatch Sequence Is a Revenue Decision, Not Just a Logistics Problem

**Status:** Pattern
**Domain:** Field operations / dispatch
**Applies to:** `skilled-trades-contracting`

---

## Why this exists

Dispatch decisions — which technician goes to which call in which order — are made primarily on geography and technician availability. They are also revenue decisions: different technicians have different close rates, different average tickets, and different customer satisfaction scores. A service call with a high-probability-of-replacement outcome should be dispatched to the technician with the highest replacement close rate, not just the nearest available truck. A maintenance agreement renewal call should go to the technician with the best customer-retention record. Dispatchers who treat all calls as equivalent and all technicians as interchangeable are leaving revenue on the table with every dispatch decision.

## How to apply

Build a call-classification and technician-matching protocol:

```
Dispatch routing matrix:
  Call type classification:
    Emergency repair:      first available, closest — speed dominates
    Non-emergency repair:  match to technician close rate for that equipment type
    Replacement estimate:  dispatch highest-close-rate technician
    Maintenance visit:     dispatch the same technician the customer knows (retention)
    New construction:      match to experience level with the project scope

  Technician performance profile (update monthly):
    Technician:      ______
    Close rate on replacement estimates: ______%
    Average ticket (service):            $______
    Maintenance renewal rate:            ______%
    Customer satisfaction score:         ______
    Primary equipment strength:          ______

  Dispatch decision criteria:
    Revenue-critical calls (replacement estimates, high-value service):
      Route to top-close-rate technician within schedule constraints.
    Retention-critical calls (agreement renewal, complaint follow-up):
      Route to familiar technician or highest-CSAT technician.
    Standard service calls:
      Route geographically for efficiency; hold revenue-critical criteria for high-value calls.
```

**Do:**
- Track close rate, average ticket, and CSAT by technician in the dispatch system — these are the routing inputs, not just performance review inputs.
- Define "revenue-critical" calls explicitly in the dispatch protocol (e.g., any call where the system is >10 years old and likely a replacement candidate).
- Communicate the routing rationale to technicians; the ones who earn the replacement calls should understand why.

**Don't:**
- Route all calls purely by geographic proximity without considering call type and technician strength — the closest technician is not always the most valuable technician for the job.
- Let the dispatch system default to "first available" without a call-classification override for high-value opportunities.

## Edge cases / when the rule does NOT apply

Same-day emergency HVAC calls in peak season — when every technician is already dispatched and a customer has no heat or cooling — dispatch is constrained by availability, not optimization. For these calls, speed is the only criterion.

## See also

- [`../agents/field-operations-specialist.md`](../agents/field-operations-specialist.md) — owns the dispatch protocol and technician performance tracking.
- [`../agents/trade-business-analyst.md`](../agents/trade-business-analyst.md) — owns the per-technician revenue metrics that feed the dispatch routing decision.
- [`./billable-hour-efficiency-is-the-fields-master-number.md`](./billable-hour-efficiency-is-the-fields-master-number.md) — geographic dispatch efficiency affects billable-hour ratio; the two rules must be balanced against each other.

## Provenance

Revenue-weighted dispatch is a documented practice in HVAC and service-contractor field management; the close-rate-based routing approach is covered in Nexstar Network and Service Nation contractor training programs.

---

_Last reviewed: 2026-06-05 by `claude`_
