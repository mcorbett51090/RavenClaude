# Staff to the traffic curve, not the clock

**Status:** Absolute rule
**Domain:** Labor scheduling, workforce management
**Applies to:** `retail-store-operations`

---

## Why this exists

A schedule built around clock-based shifts (8 am–4 pm, 12 pm–8 pm) treats all hours as
equally valuable. They are not. A Saturday midday peak may drive 3× the hourly transaction
volume of a Tuesday morning opening. A flat-shift schedule systematically:

- **Under-staffs peak blocks** where conversion opportunity is highest and one additional
  associate meaningfully increases basket capture.
- **Over-staffs valley blocks** where incremental associates add labor cost with no conversion
  return.

The result is a schedule that feels busy (hours are filled) but performs poorly (SPLH and
conversion rate are below potential). The fix is to design shifts to match the traffic curve:
peak-layer shifts, flex 4–5 hour shifts on the highest-traffic blocks, task work in valleys.

## How to apply

1. Collect hourly traffic or transaction data (minimum 4 weeks).
2. Compute the hourly traffic index (hour volume ÷ daily average) by day-of-week.
3. Identify peak blocks (index ≥ 1.5), valley blocks (index ≤ 0.6), and transitions.
4. Design shift shapes to match: opening coverage, peak layers, flex shifts on peak blocks,
   task and stocking work in valleys.
5. Cross-check: total scheduled hours × average wage ÷ projected sales = labor %.

Use `scripts/retail_calc.py` `sales_per_labor_hour` to verify SPLH.

**Do:**

- Require hourly traffic or transaction data before building or approving a schedule.
- Put flex (shorter) shifts on peak blocks, not opening coverage.
- Schedule task work — stocking, receiving, markdowns — in valley windows only.
- Track SPLH and conversion rate by hour block as the quality metrics for the schedule.

**Don't:**

- Build a schedule as a set of 8-hour shifts distributed evenly across the week.
- Cut peak-block hours to hit a labor % target — this trades conversion for a budget line.
- Accept "we've always done it this way" as a reason to keep a flat-shift structure.

## Edge cases / when the rule does NOT apply

- **Regulatory minimums:** predictive scheduling ordinances may constrain shift shape changes
  (advance notice, minimum hours guarantees). Comply with the ordinance; optimize within it.
- **Overnight restocking formats** (some grocery, big-box): task work dominates and is by design
  in off-peak hours. The traffic-curve principle still applies to customer-facing shifts; task
  shifts follow a different optimization.
- **Very low-traffic stores:** when hourly variation is small (index range 0.8–1.2 all day),
  a flat schedule may be appropriate. Verify with actual traffic data before concluding this.

## See also

- [`./omnichannel-inventory-is-one-pool.md`](./omnichannel-inventory-is-one-pool.md)
- [`../knowledge/retail-store-operations-decision-trees.md`](../knowledge/retail-store-operations-decision-trees.md) (Staff-to-traffic tree)
- [`../skills/labor-scheduling/SKILL.md`](../skills/labor-scheduling/SKILL.md)
- [`../scripts/retail_calc.py`](../scripts/retail_calc.py)

## Provenance

Traffic-curve scheduling is the foundation of demand-driven labor models deployed by most
major specialty and department store retailers. The underlying principle is documented in NRF
workforce management publications and is the core design logic of platforms like Legion WFM
and UKG Retail Scheduling.

---

_Last reviewed: 2026-06-08 by `claude`._
