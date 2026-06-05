# Order Quality Index Before Recruiter Performance Review

**Status:** Primary diagnostic
**Domain:** Staffing operations
**Applies to:** `staffing-operations`

---

## Why this exists

A recruiter with low placements may be under-fed with unworkable orders rather than under-performing. If the order quality index — the proportion of active orders that are workable, competitively priced, and within the firm's service scope — is poor, then the recruiter is being measured against a broken input. A performance review that doesn't first rule out order quality is not a performance review; it is blame assignment.

## How to apply

Calculate the order quality index before pulling any recruiter performance analysis:

```
Order Quality Index (per desk or division)
───────────────────────────────────────────
Period:  ________________
Division / recruiter desk:  ________________

Total active orders:                  ___
  Less: on-hold / suspended:          ___
  Less: uncompetitive bill rate:       ___  (criteria: ___% below market)
  Less: aged beyond [X] days:          ___  (aged threshold: ___ days)
  Less: out-of-scope / unserviceable: ___
Workable orders:                      ___

Order quality index:  workable ÷ total active = ___%  [target: ≥ 70% workable]

Recruiter-to-workable-order ratio:
  Recruiters on desk:     ___
  Workable orders:        ___
  Ratio:                  ___  workable orders per recruiter  [healthy range: 8–15 for travel nursing; varies by segment]

Interpretation:
  [ ] OQI ≥ 70%: order quality supports recruiter performance review
  [ ] OQI < 70%: fix orders before evaluating recruiters
```

**Do:**
- Run the order quality index at the division or desk level before any recruiter performance conversation.
- Separate uncompetitive bill rates from aged orders in the OQI — they have different fixes (pricing vs. intake discipline).
- Share the OQI results with the recruiter in the performance conversation — a recruiter who can see the order quality data is more likely to engage constructively.

**Don't:**
- Use total active orders as the denominator for recruiter productivity metrics — it inflates the workload and makes performance look worse than it is on workable orders.
- Declare an order quality problem "fixed" until the OQI is re-calculated after corrections — verbal commitments to improve bill rates don't change the index.
- Compare recruiter performance across desks with different OQIs without adjusting for it.

## Edge cases / when the rule does NOT apply

In a direct-hire or search-fee model, the concept of an order quality index adapts to a search quality index (are the searches scoped to win?). The principle — feed quality before recruiter performance — is universal.

## See also

- [`../agents/staffing-operations-analyst.md`](../agents/staffing-operations-analyst.md) — owns the OQI calculation as part of the diagnostic workflow.
- [`./split-supply-from-order-quality-before-blaming-recruiters.md`](./split-supply-from-order-quality-before-blaming-recruiters.md) — the governing rule on separating supply from order-quality drivers.

## Provenance

Codifies CLAUDE.md §3 #4 (diagnose the funnel before blaming the recruiter) with a specific order-quality index instrument. The workable-order segmentation is a standard staffing operations diagnostic used in ops-consulting engagements [unverified — training knowledge].

---

_Last reviewed: 2026-06-05 by `claude`_
