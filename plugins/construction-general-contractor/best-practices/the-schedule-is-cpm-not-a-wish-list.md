# The schedule is CPM, not a wish list

**Status:** Pattern
**Domain:** CPM scheduling and project delivery
**Applies to:** `construction-general-contractor`

---

## Why this exists

A Gantt chart with no logic ties is a list of dates with no causal relationship between them.
It cannot identify the critical path, it cannot support a delay claim, and it cannot tell you
whether a disruption actually affected the project completion date. Many GCs produce Gantt
bar charts and call them "schedules." They work until something goes wrong — at which point the
owner's scheduler produces a real CPM network and the GC has nothing to argue from. A properly
built CPM schedule is the GC's primary contract management tool and its primary delay-claim
instrument.

## How to apply

- Every activity has a predecessor and a successor. No exceptions except the project start
  milestone (no predecessor) and the project finish milestone (no successor).
- Calculate the critical path mathematically (forward pass / backward pass). Don't guess
  which activities are critical.
- Maintain the baseline and update the schedule weekly. The delta between baseline and
  current is the schedule variance — this is the record.
- Integrate submittal lead times as activities in the CPM. A submittal chain that's not in
  the schedule is a hidden critical-path risk.

**Do:**

- Compute durations from quantity ÷ productivity. Document the productivity assumption.
- Use SS and FF relationships with lags only where real field constraints require them;
  document the reason.
- Establish a locked baseline before work starts.
- Update the critical path in every weekly update. Note if the critical path shifts.
- Keep the look-ahead schedule aligned with the CPM.

**Don't:**

- Submit a schedule with activities that have no predecessor or no successor (except start/
  finish milestones).
- Use inflated durations or hidden lags to manufacture float.
- Treat float as the GC's private reserve without disclosing it.
- Reconstruct delay analysis from memory months after the fact.

## Edge cases / when the rule does NOT apply

Very small projects (under 60 days / under 5 major activities) and interior tenant-improvement
work with a single trade sequence may be managed with a simplified bar chart provided the
contract does not require CPM. Always check the contract — many public and institutional
owners specify CPM scheduling explicitly (often with P6 as the required tool).

## See also

- [`../skills/cpm-scheduling/SKILL.md`](../skills/cpm-scheduling/SKILL.md)
- [`../knowledge/construction-gc-decision-trees.md`](../knowledge/construction-gc-decision-trees.md) — Critical-path-impact tree
- [`./every-change-is-documented-before-the-work.md`](./every-change-is-documented-before-the-work.md)

## Provenance

CPM (Critical Path Method) was developed by DuPont in the 1950s and is codified in AACE
International's Recommended Practices for project scheduling. AACE RP 29R-03 (Forensic
Schedule Analysis) is the reference standard for delay analysis methodology.

---

_Last reviewed: 2026-06-08 by `claude`._
