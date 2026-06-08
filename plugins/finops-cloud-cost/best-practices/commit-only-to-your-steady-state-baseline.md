# Commit only to your steady-state baseline

**Status:** Absolute rule
**Domain:** Cloud commitment management (Reserved Instances, Savings Plans, Committed Use Discounts)
**Applies to:** `finops-cloud-cost`

---

## Why this exists

A commitment (RI, Savings Plan, CUD) is a billing contract: you pay for a level of usage whether
or not you actually use it. Over-committing — buying commitments that exceed the actual steady-state
baseline — converts a discount into a stranded cost. The commitment you bought for an instance that
was decommissioned 6 months into a 1-year term is not a saving; it is a penalty.

The steady-state baseline is the P0 floor — the usage that would have occurred anyway in your worst
week. It is not the average (which includes peaks), not the P90 (which is the rightsizing target for
the instance size, not the commitment level), and not the peak. Committing above the floor means
betting that usage will never drop below the commitment level — a bet that rarely holds over a 1-
or 3-year term in a growing or changing organization.

## How to apply

1. Run a rightsizing pass first (see `rightsize-before-you-commit.md`). The commitment baseline
   must be calculated on the rightsized instance sizes, not the current over-sized fleet.
2. Identify the P0 floor from 14–30 days of hourly utilization data: the minimum consistent
   hourly resource consumption across the measurement period.
3. Use `scripts/finops_calc.py commitment_coverage()` to calculate what percentage of current
   usage the P0 floor represents.
4. Purchase commitments at or below the P0 floor level. The remainder runs on-demand or spot.
5. Use `finops_calc.py break_even()` to validate the commitment pays back within an acceptable
   horizon. For a 1-year no-upfront RI, break-even is typically 6–9 months [verify-at-use]; if
   break-even exceeds the term, the commitment is not justified.
6. Commit to the floor, on-demand the ceiling.

**Do:**

- Calculate the steady-state baseline from real utilization data, not from capacity planning
  estimates.
- Document the baseline measurement period and the P0 value alongside every commitment purchase.
- Re-evaluate commitments quarterly — a baseline can shrink (decommissions, efficiency improvements)
  or grow (headroom for new commitments).
- Track commitment utilization as a FinOps KPI. Utilization <80% on a commitment is a signal of
  over-commitment.

**Don't:**

- Buy commitments based on the average utilization or the peak — those metrics over-commit.
- Purchase 3-year commitments for workloads whose future is uncertain (fast-growing, fast-changing,
  pilot/experiment stage).
- Delegate commitment purchases to an automated tool without verifying the steady-state baseline it
  is using.
- Treat RI/SP recommendations from provider consoles as pre-approved — they optimize for your
  savings relative to on-demand, not for your risk of over-commitment.

## Edge cases / when the rule does NOT apply

For purely dedicated, business-critical workloads (e.g., a production database that has run at
a stable utilization level for 3+ years and is contractually required), a 3-year commitment at
the measured baseline is reasonable. The key qualifiers: the baseline is measured, the workload
is stable, and the commitment is at the baseline, not above it.

## See also

- [`./rightsize-before-you-commit.md`](./rightsize-before-you-commit.md)
- [`../skills/rightsizing-and-commitments/SKILL.md`](../skills/rightsizing-and-commitments/SKILL.md)
- [`../knowledge/finops-cloud-cost-decision-trees.md`](../knowledge/finops-cloud-cost-decision-trees.md) — commitment-vs-on-demand tree

## Provenance

Codifies the FinOps Foundation optimize-phase commitment management guidance and the practical
discipline of separating the commitment target (P0 floor) from the rightsizing target (P90 band).

---

_Last reviewed: 2026-06-08 by `claude`._
