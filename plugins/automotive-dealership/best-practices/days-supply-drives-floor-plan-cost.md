# Days-supply drives floor-plan cost

**Status:** Pattern
**Domain:** Inventory management, variable ops
**Applies to:** `automotive-dealership`

---

## Why this exists

Every vehicle on a dealership's lot is financed through a floor-plan line of credit. The
daily interest cost is real and compounding: `(vehicle balance × annual rate) ÷ 365`.
On a $30,000 used vehicle at a 7% annual floor-plan rate [verify-at-use], that is ~$5.75/day.
On a 100-unit used lot, that is ~$575/day in floor-plan expense alone — not counting lot
insurance, opportunity cost, or reconditioning capital. Days-supply is not a vanity metric;
it is a direct driver of the floor-plan line on the P&L.

The right days-supply target is segment-specific and brand-specific — not "lower is always
better." An under-supplied used-car lot loses turns and gross because customers don't find
their vehicle. The discipline is to right-size supply to turn rate, not to minimize at all
costs.

## How to apply

Set days-supply targets by segment (not just for the whole lot). Manage to the target with
a weekly inventory aging report.

**Do:**

- Calculate days-supply by segment weekly: `Units on hand ÷ (30-day retail rate ÷ 30)`.
- Set a written days-supply target per segment, reviewed quarterly.
- Use an aging report with buckets (0–30, 31–60, 61–90, 90+ days) and attach a cost to
  each bucket: `Units in bucket × average holding cost × days`.
- Establish a wholesale date for every unit that crosses 60 days — not a hope, a date.
- Use market data (Manheim MMR, vAuto Provision, or equivalent [verify-at-use]) to price
  units to market within days of acquisition.

**Don't:**

- Use OEM-suggested stocking levels as a substitute for your actual turn rate.
- Hold over-age units without an explicit plan (price reduction schedule or wholesale date).
- Source inventory based on what is cheap at auction rather than what is turning in
  your market segment.
- Measure days-supply only in aggregate — a 45-day overall average can hide 90-day SUVs
  and 15-day compacts.

## Edge cases / when the rule does NOT apply

For limited-production or high-demand units (e.g., a hot-commodity trim in an
undersupplied market), holding above the target days-supply while demand supports above-
market gross may be justified — but requires active monitoring. The floor-plan cost math
still applies; the justification is a higher expected gross that more than offsets it.
Document the exception explicitly rather than applying it as a blanket "we sell a lot of
these so we carry a lot of them."

## See also

- [`./recon-time-is-holding-cost.md`](./recon-time-is-holding-cost.md)
- [`../knowledge/automotive-dealership-decision-trees.md`](../knowledge/automotive-dealership-decision-trees.md)
  (Hold-vs-wholesale tree)
- [`../skills/inventory-and-desking/SKILL.md`](../skills/inventory-and-desking/SKILL.md)
- [`../scripts/dealer_calc.py`](../scripts/dealer_calc.py) — `days_supply` and
  `recon_holding_cost` modes

## Provenance

Standard inventory management discipline documented in NADA used-vehicle management guides,
vAuto/Cox Automotive training, and dealer 20-group performance benchmarking programs.
Floor-plan rates and target days-supply ranges vary by market and lender [verify-at-use].

---

_Last reviewed: 2026-06-08 by `claude`._
