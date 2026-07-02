# A comeback costs you twice

**Status:** Absolute rule
**Domain:** Quality / bay workflow
**Applies to:** `auto-repair-shop-operations`

> Advisory operations rule. Comeback-rate benchmarks are `[verify-at-use]`. No customer PII.

---

## Why this exists

A comeback is the most expensive event in the shop because it charges you twice. First, the **rework hour**: labor billed at zero but still paid to the technician and still occupying a bay that could hold a paying job — a direct hit to the effective labor rate and to car-count capacity. Second, the **customer**: a vehicle that comes back erodes the trust that drives recall and referral, the cheapest car count a shop has. A shop that re-fixes comebacks without finding *why* they came back will see the same pattern return, quarter after quarter, silently taxing labor gross profit.

## How to apply

- Group every comeback by **root cause** — misdiagnosis, workmanship, part quality, incomplete repair, no-fault — and fix the process that produced the group.
- Make the technician who caused a **workmanship** comeback own the rework (billed at zero); that is the incentive that protects quality under a flat-rate pay plan.
- Stage parts before dispatch so a parts-hold never becomes a cold-vehicle re-diagnosis.
- Add a QC / multi-point verification step before closeout; track first-time-fix rate as the inverse of comeback rate.

**Do:** triage by cause; fix the process; own the rework.
**Don't:** re-fix the car without finding why; let the rework bill as new work; chase comebacks one at a time.

## Edge cases / when the rule does NOT apply

A **no-fault** return (an unrelated new concern, or a customer expectation set poorly at write-up) is not a quality comeback — it's a new RO and, often, a write-up-clarity fix. Classify it honestly rather than forcing it into the workmanship bucket.

## See also

- [`../skills/ro-lifecycle-and-comeback-control/SKILL.md`](../skills/ro-lifecycle-and-comeback-control/SKILL.md), [`../skills/technician-productivity-and-efficiency/SKILL.md`](../skills/technician-productivity-and-efficiency/SKILL.md)
- Command: [`../commands/diagnose-comebacks.md`](../commands/diagnose-comebacks.md)

## Provenance

Codifies `technician-workflow-manager` house opinion and the comeback-root-cause decision tree. Benchmarks: [`../knowledge/auto-repair-shop-reference-2026.md`](../knowledge/auto-repair-shop-reference-2026.md) (verify-at-use).

---

_Last reviewed: 2026-07-02 by `claude`_
