# Omnichannel inventory is one pool

**Status:** Pattern
**Domain:** Inventory management, BOPIS, omnichannel fulfillment
**Applies to:** `retail-store-operations`

---

## Why this exists

A physical store that participates in BOPIS (Buy Online, Pick Up In Store) or ship-from-store
fulfillment is drawing on the same physical inventory as walk-in customers. The shelf does not
know whether a unit will be picked by a customer who walked in or by a picker filling an online
order. When a retailer manages store inventory and BOPIS inventory as separate pools — or when
the BOPIS system shows inventory without accounting for concurrent walk-in demand — three failure
modes emerge:

1. **BOPIS cancellations:** the online channel commits to a unit that a walk-in customer
   already purchased, or that phantom inventory made look available. Cancel rates climb;
   NPS falls; the customer buys elsewhere.
2. **Walk-in stockouts:** aggressive BOPIS fulfillment depletes the shelf faster than
   replenishment expects, creating a stockout for walk-in customers that the inventory system
   doesn't flag as an OOS event.
3. **Inventory accuracy collapse:** BOPIS picks that aren't correctly reconciled to on-hand
   counts, or cancellations that aren't reactivated in the system, create compounding accuracy
   errors that distort replenishment signals.

The correct mental model is one inventory pool with two demand streams — and the management
system must account for both.

## How to apply

**Do:**

- Design replenishment models that account for BOPIS demand velocity, not just walk-in sales.
- Set an inventory buffer for BOPIS-eligible SKUs: reduce BOPIS-available quantity by a
  buffer factor (typically 10–20% of on-hand) to absorb phantom inventory and concurrent demand.
- Track BOPIS cancel rate by SKU. A SKU with > 5% cancel rate needs an immediate cycle count
  and a BOPIS-eligibility review.
- Prioritize BOPIS-eligible SKUs in A-tier cycle counts — phantom inventory here creates the
  most customer-facing impact.
- Use pick-confirmation workflows before committing BOPIS fulfillment.

**Don't:**

- Launch BOPIS fulfillment without a buffer, a cancel-rate KPI, or a cycle-count program.
- Treat walk-in OOS and BOPIS OOS as separate KPIs that are never compared — they draw from
  the same pool and affect each other.
- Assume BOPIS cancel-rate is a "digital" problem owned by the e-commerce team — it is an
  in-store inventory accuracy problem.

## Edge cases / when the rule does NOT apply

- **Dedicated BOPIS inventory sections:** some high-volume formats hold a separate, physically
  segregated quantity reserved for BOPIS fulfillment. This is a legitimate design that manages
  the one-pool problem through physical separation. It changes the replenishment model (now
  two sub-pools) but does not change the underlying principle — both pools still draw from
  the same receiving and shrink exposure.

## See also

- [`./shrink-has-a-root-cause-find-it.md`](./shrink-has-a-root-cause-find-it.md)
- [`../skills/inventory-and-replenishment/SKILL.md`](../skills/inventory-and-replenishment/SKILL.md)
- [`../agents/inventory-and-replenishment-analyst.md`](../agents/inventory-and-replenishment-analyst.md)
- Seam: online/DTC omnichannel strategy → `ecommerce-dtc`

## Provenance

The BOPIS inventory-accuracy problem and the one-pool design principle are documented in NRF
omnichannel research and retail operations literature. The BOPIS cancel-rate metric and its
connection to inventory accuracy have been widely reported in retail analyst coverage since
the acceleration of BOPIS adoption in 2020–2022.

---

_Last reviewed: 2026-06-08 by `claude`._
