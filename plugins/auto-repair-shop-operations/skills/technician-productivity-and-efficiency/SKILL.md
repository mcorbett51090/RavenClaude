---
name: technician-productivity-and-efficiency
description: "Diagnose a repair shop's labor throughput with the three distinct dials: productivity (clocked/available), efficiency (billed/clocked), and proficiency (billed/actual). Match dispatch to skill, read them separately, and fix the right one. Benchmarks verify-at-use; no PII."
---

# Technician Productivity & Efficiency

Billed hours — the input to labor gross profit — come from technicians who are present, busy, and fast. Those are **three different measurements**, and prescribing without knowing which one is low wastes the fix.

> **Advisory, operations decision-support.** Productivity/efficiency/proficiency benchmark ranges are volatile and shop-specific — every target here is `[verify-at-use]` against the shop's own baseline. No customer PII.

## The three dials (never blend them)

| Dial | Formula (concept) | Reads | If low, look at |
|---|---|---|---|
| **Productivity** | clocked hours / available hours | Is the tech on a job at all? | Dispatch, car count, parts-hold, idle time |
| **Efficiency** | billed (flagged) hours / clocked hours | Is the tech beating flag time? | Skill match, tooling, information/labor-guide access |
| **Proficiency** | billed hours / actual hours on the job | True speed vs the guide | Training, diagnostic process, comebacks |

**The rule:** diagnose the specific dial before prescribing. A tech at 100% efficiency but 60% productivity is idle, not slow — a dispatch/car-count problem, not a skills problem. A busy shop with low efficiency has a throughput problem, not a capacity problem.

## Dispatch to skill

Match job difficulty to tech level (master/general/lube or A/B/C). A diagnostic on a junior bench is slow and comeback-prone; an oil change on the A-tech is billable expertise thrown away. Dispatch discipline is often the cheapest productivity gain in the building.

## Metrics

| Metric | Reads | Note |
|---|---|---|
| Productivity % | clocked / available | Low → dispatch, staging, or car-count gap |
| Efficiency % | billed / clocked | The labor-GP multiplier `[verify-at-use]` |
| Proficiency % | billed / actual | Training/tooling signal |
| Hours billed per tech per day | billed hours / techs | The floor's output number |

## Anti-patterns

- Reporting one blended "productivity" number that hides which dial is broken.
- Adding a tech to fix low efficiency (a throughput problem, not a headcount one).
- Leaving the A-tech on lube work because they're reliable.

## See also

- Traverse the **comeback root-cause triage** and **tech pay: flat-rate vs hourly** trees in [`../../knowledge/auto-repair-shop-decision-trees.md`](../../knowledge/auto-repair-shop-decision-trees.md).
- [`../effective-labor-rate-and-gross-profit/SKILL.md`](../effective-labor-rate-and-gross-profit/SKILL.md) (billed hours feed labor GP), [`../ro-lifecycle-and-comeback-control/SKILL.md`](../ro-lifecycle-and-comeback-control/SKILL.md).
- Best practices: [`../../best-practices/schedule-the-bay-not-the-day.md`](../../best-practices/schedule-the-bay-not-the-day.md).
