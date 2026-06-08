# Recon time is holding cost

**Status:** Pattern
**Domain:** Used-vehicle operations, fixed ops
**Applies to:** `automotive-dealership`

---

## Why this exists

Every day a used vehicle sits in reconditioning is a day it is not on the retail lot,
priced to sell, generating gross. The floor-plan meter runs during recon. The opportunity-
cost meter also runs: a day in recon is a day the vehicle cannot be appraised by a potential
buyer. Recon is not a cost center to be minimized — it is a throughput process to be
managed with time SLAs and cost controls, because its speed directly determines used-
vehicle gross margin.

A 10-unit used-vehicle store that averages 8 days in recon vs a competitor at 4 days is
carrying double the in-process holding cost and reaching the retail lot 4 days later per
unit. At $30/day holding cost per unit and 10 units, that is $300/day, or $9,000/month,
in additional holding cost that comes directly off used-car gross.

## How to apply

Treat recon as a profit lever with a written SLA, a cost cap per unit, and a weekly
throughput report.

**Do:**

- Set a written recon time SLA: acquisition-to-retail-ready in ≤5 business days is a
  common target [verify-at-use]. Measure and report it weekly.
- Set a per-unit recon cost budget and a cost-authorization threshold (e.g., >$1,000
  recon requires used-car manager approval).
- Track recon-in-process units separately from lot inventory in the days-supply report.
- Run the hold-vs-wholesale decision on any unit where recon estimate + remaining holding
  cost exceeds the break-even threshold (see the decision tree).
- Establish a fixed-ops / used-car department service agreement: priority scheduling for
  used-car recon, with committed turnaround times.
- Price the internal RO at full posted rate — the subsidy is a transfer, not a discount.

**Don't:**

- Let recon proceed without a written estimate and approval for costs over the threshold.
- Count recon-in-process units in the "on lot" days-supply figure — they are not retail-ready.
- Allow recon to run indefinitely on a unit that should be wholesaled — the recon decision
  is a financial decision, not a mechanical one.
- Use "it's our own car" to justify below-posted-rate internal RO pricing.
- Celebrate low recon cost without checking recon time — a cheap recon that takes 14 days
  is more expensive than a slightly pricier one done in 4 days.

## Edge cases / when the rule does NOT apply

Certified pre-owned (CPO) recon under an OEM CPO program has inspection requirements that
set a floor on recon standards and may increase both cost and time. The SLA discipline still
applies, but the cost floor is OEM-defined. In high-volume auction buys (large lot
purchases), batch recon may justify a different throughput model — but the per-unit cost
and total-batch time discipline remains.

## See also

- [`./days-supply-drives-floor-plan-cost.md`](./days-supply-drives-floor-plan-cost.md)
- [`../knowledge/automotive-dealership-decision-trees.md`](../knowledge/automotive-dealership-decision-trees.md)
  (Hold-vs-wholesale tree)
- [`../skills/inventory-and-desking/SKILL.md`](../skills/inventory-and-desking/SKILL.md)
- [`../scripts/dealer_calc.py`](../scripts/dealer_calc.py) — `recon_holding_cost` mode

## Provenance

Standard used-vehicle management discipline documented in NADA used-vehicle management
guides, vAuto/Cox Automotive training, and dealer performance consulting frameworks.
Specific SLA targets (5 business days) are industry convention — verify against your
current market and OEM CPO requirements [verify-at-use].

---

_Last reviewed: 2026-06-08 by `claude`._
