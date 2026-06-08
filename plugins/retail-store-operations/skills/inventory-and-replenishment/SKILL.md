---
description: "Run a store inventory accuracy and replenishment design: diagnose out-of-stocks and phantom inventory, set replenishment triggers (reorder point, safety stock with explicit service-level target), design a cycle-count program, and build BOPIS inventory integrity controls."
---

# Inventory and Replenishment

**Purpose:** produce a replenishment design or inventory accuracy plan where every trigger has
an explicit service-level target, every phantom-inventory diagnosis has a root cause, and every
BOPIS decision accounts for the shared inventory pool.

---

## Entry-point playbook

### Step 1 — Baseline inventory accuracy

| Input | Why it matters |
|---|---|
| System on-hand (SOH) vs. physical count | Accuracy baseline — needed before any replenishment fix |
| Shrink rate by category | Quantifies how much inventory disappears between counts |
| Out-of-stock rate (% of SKUs with zero available and recent sales) | Demand signal |
| BOPIS cancel rate | Proxy for phantom inventory on BOPIS-eligible SKUs |
| Last cycle count or physical inventory date | Data freshness |

If accuracy data is unavailable, the first recommendation is always a targeted cycle count —
not a replenishment redesign.

### Step 2 — Separate phantom from true OOS

**Phantom inventory:** system shows on-hand, shelf is empty.

Root causes: shrink not yet booked, receiving error (received but not scanned), mis-pick in
backroom, wrong floor location in system, inter-store transfer not updated.

**True OOS:** system is zero or near-zero and the shelf is empty.

Root causes: replenishment trigger too low, reorder frequency too slow, supplier lead time
increased, demand spike not anticipated.

Fix the accuracy problem before adjusting replenishment triggers — a replenishment model running
on phantom inventory will over-order.

### Step 3 — Design replenishment triggers

For each SKU class (A/B/C by velocity):

| Parameter | Formula / Source |
|---|---|
| Average daily sales | Rolling 4–8 week average, adjusted for seasonality |
| Lead time (days) | DC-to-store transit + processing time |
| Reorder point | (Avg daily sales × lead time) + safety stock |
| Safety stock | z-score × σ(demand) × √(lead time) — or simpler: days of cover at target service level |
| Service-level target | **Must be stated explicitly:** 95% / 98% / 99% in-stock |
| Reorder quantity | Economic order quantity or vendor pack-size constrained |

Use [`../../scripts/retail_calc.py`](../../scripts/retail_calc.py) `weeks_of_supply` mode to
verify WOS at the reorder point.

**A replenishment trigger with no service-level target is not a design — it is a number.**
Always state the service level the trigger is designed to achieve.

### Step 4 — ABC cycle count design

| Tier | Criteria | Count frequency |
|---|---|---|
| A | Top 20% of velocity; BOPIS-eligible; high shrink | Weekly |
| B | Next 30% of velocity | Monthly |
| C | Remaining; slow movers | Quarterly |

Prioritize A-tier cycle counts on BOPIS-eligible SKUs — phantom inventory here generates direct
BOPIS cancellations and NPS events.

Variance tolerance: set a recount threshold (e.g., variances > 10% of on-hand or > 5 units
trigger an immediate recount and shrink investigation).

### Step 5 — BOPIS inventory integrity

BOPIS-eligible SKUs need an inventory buffer:

- **Buffer logic:** reduce BOPIS-available quantity by a buffer factor (e.g., 15–20% of on-hand)
  to absorb phantom inventory and concurrent pick conflicts.
- **Pick confirmation:** require physical confirmation before fulfillment is committed.
- **Cancel-rate KPI:** track by SKU and store; a SKU with > 5% cancel rate gets cycle-counted
  immediately and removed from BOPIS eligibility until accuracy is restored.

### Step 6 — Replenish vs. allocate decision

Traverse the replenish-vs.-allocate tree in
[`../../knowledge/retail-store-operations-decision-trees.md`](../../knowledge/retail-store-operations-decision-trees.md)
to determine whether the store should trigger a reorder (store-initiated pull) or wait for a
DC-pushed allocation.

### Step 7 — Output artifact

Include: accuracy baseline (SOH accuracy %), OOS rate, phantom vs. true OOS split, service-level
target, replenishment trigger parameters, cycle-count program design (A/B/C), BOPIS controls.

---

## Anti-patterns

- Redesigning replenishment without first establishing inventory accuracy.
- Safety stock with no service-level target.
- A cycle count program without ABC segmentation — all SKUs counted at the same frequency
  wastes effort on slow movers while fast movers miss counts.
- BOPIS launched without a buffer and a cancel-rate KPI.
- A replenishment "fix" for phantom inventory — accuracy must precede the trigger redesign.

---

## Output

An inventory deliverable from this skill always contains:

1. **Accuracy baseline** (SOH % accurate or "unknown — cycle count required").
2. **OOS rate** and phantom vs. true OOS classification.
3. **Replenishment triggers** with reorder point, safety stock, and **stated service-level target**.
4. **Cycle-count program** (ABC tiers, frequencies, variance tolerance).
5. **BOPIS controls** (buffer, pick confirmation, cancel-rate KPI) if BOPIS is in scope.
6. **Handoff flags:** merchandising-analyst if the OOS is a planogram/assortment issue;
   loss-prevention-advisor if phantom inventory suggests unbookmarked shrink.
