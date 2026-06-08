---
name: truck-stock-and-parts
description: "Design, rationalize, and optimize truck-stock for field-service technicians — tier the parts list by usage frequency and service-level impact, set reorder points, model the first-time-fix ↔ carrying-cost tradeoff, and analyze parts-delay failures and returns."
---

# Truck Stock and Parts

**Purpose:** treat the technician's truck as a mobile warehouse with a service-level target —
decide which parts to carry, at what quantities, with what reorder logic, to maximize first-time-fix
rate at a defensible carrying cost.

---

## Steps

### 1. Classify the parts universe into three tiers

Before deciding what to stock, tier every part by usage frequency and service-level impact:

| Tier | Criteria | Stocking rule |
|---|---|---|
| **Universal carry** | Used ≥ 1×/month per tech; failing to have it routinely causes first-time-fix misses; low-to-mid unit cost | Every truck carries min/max quantities; reordered at min |
| **Tech-specialty** | Used < 1×/month; required for the technician's specific equipment authorization or job type | Tech carries based on their scheduled job types; pre-staged per job if not on truck |
| **Special-order** | Low frequency (< 4×/year per fleet); high cost; or bulky/heavy | Not on truck; pulled from depot or ordered per-job; pre-dispatch confirmation required |

Apply the stock-the-part-or-not tree in `knowledge/fsm-decision-trees.md` to each ambiguous part.

### 2. Set fill-rate targets by SLA tier

The truck-stock fill rate must satisfy the first-time-fix target for the highest SLA tier the
technician serves:

| SLA tier served by this tech | Required truck-stock fill rate |
|---|---|
| Premium (4h response) | ≥ 95% on universal-carry parts |
| Standard (8h response) | ≥ 90% on universal-carry parts |
| Basic / best-effort | ≥ 85%; special-order pre-pull acceptable |

Use `scripts/fsm_calc.py` `truck_stock_fill_rate()` to calculate current fill rate from usage
and stockout data.

### 3. Calculate reorder points for universal-carry parts

For each universal-carry part:

```
Daily usage rate (u) = parts used per month / working days per month
Lead time (L)        = days from order to truck receipt
Safety stock (SS)    = Z × σ_u × √L   [where Z = 1.65 for 95% service level]
Reorder point (ROP)  = (u × L) + SS
Max quantity         = ROP + (u × review_period)
```

If detailed usage-variance data is unavailable, use a simpler rule: reorder at 20% of the max
quantity; set max at 2× the average monthly usage.

### 4. Analyze parts-delay failures and build the add list

From job-completion data, extract all first-time-fix misses classified as "parts unavailable."
For each part causing a miss:

1. Count the misses per month (fleet-wide).
2. Estimate the cost of a parts-delay failure: SLA penalty (if applicable) + return visit labor
   cost + customer satisfaction impact.
3. Estimate the carrying cost of adding the part to universal-carry: unit cost × average quantity
   × monthly turns.
4. Calculate payback: (monthly miss count × cost per miss) ÷ monthly carrying cost.

Rank the add list by payback period. Parts with payback < 3 months are strong add candidates.

### 5. Rationalize slow-moving and zero-moving stock

Quarterly, identify parts that have had zero or near-zero usage in the last 6 months:

1. Calculate the carrying cost (cash tied up + any expiry risk).
2. Check whether removing each part would increase the parts-delay failure rate (if the part has
   zero historical failures, removal risk is low; if it's low-frequency but high-impact when
   needed, keep it).
3. For parts flagged for removal, confirm with the `technician-productivity-analyst` that removal
   won't affect first-time-fix rate for any SLA-critical job type.
4. Return excess stock to depot or supplier (track return rate as a purchasing efficiency metric).

### 6. Implement the pre-dispatch parts-readiness check

For every job with non-universal-carry parts required:

1. At job creation, identify the parts required from the job type + equipment model.
2. Check whether those parts are on the assigned technician's truck (or at staging).
3. If not: pull from depot pre-dispatch, or order from supplier with tracking.
4. Confirm parts in hand before dispatching the technician to the job.
5. Log any job dispatched without confirmed parts as a process exception.

---

## Anti-patterns

- Stocking parts without stating the service-level target the stock level is designed to meet.
- Removing parts from truck stock without modeling the first-time-fix fill-rate impact.
- An add list that is ranked by cost to stock, not by payback (miss-cost ÷ carry-cost).
- No pre-dispatch parts-readiness check for special-order jobs.
- A return-and-excess program that removes slow-moving parts without checking their SLA
  criticality (a once-a-year part on a premium contract may be worth carrying).

---

## Output

A truck-stock design document with: the tiered parts list (universal / specialty / special-order),
the fill-rate target by SLA tier, the reorder points for universal-carry parts, the add list ranked
by payback, and the rationalization candidates with fill-rate impact noted. Reference
`scripts/fsm_calc.py` `truck_stock_fill_rate()` for all fill-rate calculations.
