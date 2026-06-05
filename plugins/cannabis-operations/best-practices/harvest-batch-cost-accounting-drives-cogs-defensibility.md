# Track cost at the harvest batch level to make COGS defensible

**Status:** Absolute rule
**Domain:** Cannabis operations / cultivation / COGS
**Applies to:** `cannabis-operations`

---

## Why this exists

The IRS's scrutiny of 280E COGS allocations lands hardest on cultivation operators who accumulate cost at the facility or period level and then apportion to harvest. Period-level cost pooling produces a COGS number an auditor can challenge by asking a single question: "show me the cost build for this specific lot." If the answer requires retrospective math, the allocation is vulnerable. Tracking cost at the harvest batch — the natural unit of cannabis production — produces a per-lot cost basis that is directly traceable to the track-and-trace system batch ID, making it audit-ready by construction.

## How to apply

Assign a cost record to each harvest batch using the batch ID from the state track-and-trace system (Metrc, BioTrack, or LeafData) as the primary key:

```
Harvest batch cost record
Batch ID (track-and-trace):    ____
Strain / room:                 ____
Harvest date:                  ____

Direct costs (accumulated during the batch cycle):
  Seeds / clones:              $____
  Nutrients / amendments:      $____
  Labor (grow cycle, harvest): $____
  Testing (mandatory):         $____
  Packaging (if applicable):   $____

Allocated costs (period overhead apportioned to batch):
  Square-footage allocation:   $____ (method: ____)
  Utilities (light, HVAC):     $____ (method: ____)
  Depreciation of fixtures:    $____ (method: ____)

Gross weight harvested:        ____g / ____lbs
Net weight after cure/trim:    ____g / ____lbs
Trim/waste:                    ____g (reconcile to track-and-trace waste log)

Cost per net gram:             $____
Cost per pound:                $____
```

Archive this record with the track-and-trace batch ID. Reconcile waste and samples to the state system entry before closing the batch cost record.

**Do:**
- Use the track-and-trace batch ID as the cost accounting key — it is the identifier an auditor will pull first.
- Accumulate direct costs in real-time as the batch cycles; retroactive accumulation inflates audit risk.
- Choose an overhead allocation method (square footage, machine hours, or canopy area) and document it in the cost accounting policy; use it consistently.

**Don't:**
- Pool all cultivation cost into a single monthly COGS figure and divide by output — this is indefensible under audit.
- Allow a failed-test batch (which generates zero saleable output) to be reallocated across passing batches without disclosing the event; it distorts per-unit cost and is a traceability issue.
- Ignore waste and sample deductions — unreconciled waste is a compliance event, not a cost-accounting convenience.

## Edge cases / when the rule does NOT apply

- Manufacturing operators (extraction, infused products) apply an analogous batch cost record keyed to the manufacturing lot ID, not the harvest ID.
- Micro-cultivators with a single-room single-strain operation may use a simplified monthly batch record, provided the track-and-trace ID still appears as the primary key.

## See also

- [`../agents/cannabis-finance-analyst.md`](../agents/cannabis-finance-analyst.md) — owns the cost model and audit-readiness review.
- [`../agents/seed-to-sale-compliance-specialist.md`](../agents/seed-to-sale-compliance-specialist.md) — owns the track-and-trace batch IDs this record keys from.
- [`./280e-makes-cogs-allocation-existential-not-academic.md`](./280e-makes-cogs-allocation-existential-not-academic.md) — the harvest batch cost record is the input to the 280E COGS allocation.

## Provenance

Derived from cannabis cultivation accounting practice, 280E compliance methodology, and track-and-trace reconciliation standards. `[unverified — training knowledge]` — validate the overhead allocation method with a licensed cannabis CPA.

---

_Last reviewed: 2026-06-05 by `claude`_
