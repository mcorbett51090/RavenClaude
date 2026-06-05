# Subcontractor Markup Must Cover Coordination Risk and Warranty Exposure

**Status:** Pattern
**Domain:** Estimating / job cost management
**Applies to:** `skilled-trades-contracting`

---

## Why this exists

Contractors who use subcontractors (electricians subbing plumbing, GCs subbing specialty trades, HVAC contractors subbing ductwork) frequently mark up the sub's cost by 10–15% and consider it a pass-through. That markup rarely covers the full cost of carrying the sub relationship: scheduling coordination, quality inspection, warranty callbacks, and the risk of being held liable to the customer if the sub fails to perform. A sub who installs ductwork incorrectly forces the general contractor to rework it at the general contractor's labor rate — often 2–3x what the original sub was paid. The markup on subcontractor cost must be built to cover this risk, not merely to cover administrative overhead.

## How to apply

Build the sub markup model with risk factors:

```
Subcontractor markup model (per sub category):
  Sub's quoted cost:                                  $______
  
  Coordination costs:
    Scheduling and inspection time (hours × rate):   $______
    Project management overhead allocation:          $______

  Risk premium:
    Sub callback / rework rate (trailing 12 months): ______% of jobs
    Average rework cost (per incident):              $______
    Expected annual rework cost / annual sub volume: ______% of sub cost
    Risk markup:                                     ______% of sub cost

  Warranty exposure:
    Customer warranty period:                        ______ years
    Sub warranty to contractor:                      ______ years (must be ≥ customer's)
    Gap exposure (if sub warranty < customer's):     price into markup

  Total markup required:
    Administrative:                                  ______%
    Coordination:                                    ______%
    Risk premium:                                    ______%
    Warranty gap:                                    ______%
    Minimum markup:                                  ______% (total)
    Target markup:                                   typically 20–35% [unverified — context-specific]

  Test: if the marked-up sub cost still produces a job margin above the target → accept sub bid.
  If not → renegotiate the sub rate or self-perform the work.
```

**Do:**
- Track sub performance (callback rate, scheduling compliance, punch-list close time) by subcontractor; use the data to differentiate markups.
- Require subs to name the general contractor as an additional insured on their GL policy — this is a pre-qualification requirement, not a negotiation.
- Verify that sub warranties to the contractor match or exceed the contractor's warranty to the customer — gaps are the contractor's liability.

**Don't:**
- Apply a blanket 10% markup to all subs regardless of performance history — high-risk subs earn a higher risk premium.
- Use a sub's timeline promise as a project schedule without a written subcontract that includes a completion date and liquidated damages for delay.

## Edge cases / when the rule does NOT apply

Specialty subcontractors who are the only licensed provider of a specific service (e.g., the local gas utility for a specific tie-in) may not be negotiable on price or markup structure; document the cost as a pass-through and price the project around it.

## See also

- [`../agents/estimating-specialist.md`](../agents/estimating-specialist.md) — owns the sub markup calculation in the estimate.
- [`../agents/field-operations-specialist.md`](../agents/field-operations-specialist.md) — tracks sub performance data (callback rate, schedule) that feeds the risk premium.
- [`./material-cost-is-the-real-cost-plus-waste-plus-markup-name-a.md`](./material-cost-is-the-real-cost-plus-waste-plus-markup-name-a.md) — sub cost has the same three-component structure as material cost; risk and markup must be explicit in both.

## Provenance

Subcontractor markup and risk management is standard in construction estimating and contracting practice; warranty chain and additional-insured requirements are covered in construction law and contractor insurance consulting.

---

_Last reviewed: 2026-06-05 by `claude`_
