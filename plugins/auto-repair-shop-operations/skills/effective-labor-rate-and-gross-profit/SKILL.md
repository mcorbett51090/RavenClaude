---
name: effective-labor-rate-and-gross-profit
description: "Read a repair shop's two profit engines separately: labor GP (effective labor rate x billed hours minus tech cost) and parts GP (the matrix over cost). Measure effective labor rate as posted rate minus discounts, warranty, comebacks, and unapplied time. Benchmarks verify-at-use; no PII."
---

# Effective Labor Rate & Gross Profit

The single most misread number in a repair shop is the labor rate. The **posted door rate** is a sign on the wall; the **effective labor rate (ELR)** is what the shop actually collects per billed hour after everything that erodes it. Profit is read on the ELR, never the door rate.

> **Advisory, operations/financial decision-support.** Rate norms, GP targets, and matrix figures are volatile and market-specific — every specific here is `[verify-at-use]` against the shop's own numbers. No customer PII.

## The two engines (read each on its own)

| Engine | Formula (concept) | Where it leaks |
|---|---|---|
| **Labor GP** | (effective labor rate x billed hours) − technician labor cost | Discounting, warranty labor at a lower rate, comeback (rework) hours billed at zero, unapplied/idle time |
| **Parts GP** | parts sale (matrix over cost) − parts cost | A flat markup instead of a tiered matrix; matrix set by the vendor, not the shop |

**The rule:** a shop can be strong on one engine and bleeding on the other. Never blend labor and parts into one "gross profit" number — diagnose them separately.

## Computing the effective labor rate

Start from the door rate and subtract every source of erosion:

1. **Discounts** — coupons, fleet/wholesale, senior, "take-care-of-'em" adjustments.
2. **Warranty labor** — often reimbursed below door rate.
3. **Comeback labor** — rework billed at zero but paid to the tech and consuming a bay.
4. **Unapplied time** — clocked hours that never make it onto an RO.

ELR = total labor dollars collected ÷ total billed hours. The **gap between door rate and ELR is recoverable margin** you're already entitled to — close it before raising the posted rate.

## Metrics

| Metric | Reads | Note |
|---|---|---|
| Effective labor rate | labor $ collected / billed hours | The real price; the number to defend |
| ELR-to-door-rate gap | door rate − ELR | The recoverable-margin opportunity |
| Labor gross profit % | labor GP / labor sales | Read against the shop's own trend `[verify-at-use]` |
| Parts gross profit % | parts GP / parts sales | Set by the matrix, not the vendor `[verify-at-use]` |

## Anti-patterns

- Reading profitability off the door rate while the ELR quietly erodes.
- Raising the posted rate to fix a discount/comeback/unapplied-time problem.
- Blending labor and parts GP so a strong parts margin hides weak labor margin (or vice versa).

## See also

- Traverse the **price a job (labor + parts matrix)** and **tech pay: flat-rate vs hourly** trees in [`../../knowledge/auto-repair-shop-decision-trees.md`](../../knowledge/auto-repair-shop-decision-trees.md).
- [`../technician-productivity-and-efficiency/SKILL.md`](../technician-productivity-and-efficiency/SKILL.md) (billed hours come from productive, efficient techs), [`../../templates/shop-kpi-dashboard.md`](../../templates/shop-kpi-dashboard.md).
- Best practices: [`../../best-practices/effective-labor-rate-is-the-real-price.md`](../../best-practices/effective-labor-rate-is-the-real-price.md), [`../../best-practices/set-the-parts-matrix-once-then-manage-it.md`](../../best-practices/set-the-parts-matrix-once-then-manage-it.md).
