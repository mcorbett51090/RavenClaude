# Move-Out Root Cause Analysis Is the Census Retention Tool

**Status:** Primary diagnostic
**Domain:** Census management / retention
**Applies to:** `senior-care-operations`

---

## Why this exists

Every move-out is a lost resident — and the question is why. Communities that track move-out reasons at a granular level can identify whether attrition is driven by avoidable causes (dissatisfaction with care, billing disputes, staff behavior, perceived value) or structural causes (death, higher acuity requiring skilled-nursing transfer, financial hardship). A community that is losing 3+ residents per month to avoidable causes but treating them all as "needs changed" is permanently destroying census without understanding it. Move-out root cause analysis is the retention analog of the denial root-cause rule: the data must exist before the fix can be targeted.

## How to apply

Conduct a structured exit process for every move-out and categorize the reason.

```
Move-out root cause taxonomy:
UNAVOIDABLE (natural attrition — no operational fix):
  - Resident death
  - Acuity too high for current level of care (transfer to skilled nursing or memory care)
  - Hospitalization with no return
  - Financial hardship (after assistance program exhausted)

POTENTIALLY AVOIDABLE (investigate each one):
  - Dissatisfied with care quality or staffing
  - Dissatisfied with management or communication
  - Family concern about safety, falls, or incidents
  - Value perception — feeling they are not getting what they pay for
  - Conflict with other residents or staff
  - Billing dispute or rate increase reaction

PROCESS (may indicate earlier detection missed):
  - Move-in acuity was higher than assessed — community was not the right fit
  - Resident or family never truly committed — chose a closer community

Tracking protocol:
  [ ] Exit interview: conducted by the Executive Director or a senior team member — not the line
      staff involved in any complaint
  [ ] 30-day follow-up call: for residents who transferred (not died) — often reveals concerns
      not shared at exit
  [ ] Monthly report: move-outs by category, % avoidable, and trend vs. prior 3 months
  [ ] Threshold alert: if avoidable move-outs exceed 25% of total move-outs in any 90-day
      period, escalate to a quality review
```

**Do:**
- Conduct the exit interview within 5 days of move-out notice — the longer the wait, the less candid the feedback.
- Separate the exit interview from any billing or administrative closure conversation — combine them and the candor disappears.
- Track avoidable move-outs as a quality metric alongside falls and incidents — they are an outcome indicator for the resident experience.

**Don't:**
- Accept "change of condition" or "family preference" as a root-cause category without probing further — these are often proxies for an avoidable cause.
- Use the move-out tracking data only in the census report; bring it into the clinical quality and staffing reviews as a leading indicator.
- Allow the same avoidable move-out reason to repeat 3+ times without a corrective action — pattern recurrence means the root cause is systemic.

## Edge cases / when the rule does NOT apply

Memory-care communities with high-acuity residents have a higher rate of unavoidable move-outs (hospitalization, death, skilled transfer) — calibrate the avoidable-rate benchmark to the segment.

## See also

- [`../agents/census-occupancy-strategist.md`](../agents/census-occupancy-strategist.md) — owns census flow analysis where move-out root cause is a primary input.
- [`./census-is-the-revenue-engine-manage-the-flow-not-just-the-nu.md`](./census-is-the-revenue-engine-manage-the-flow-not-just-the-nu.md) — move-out analysis is the retention side of the flow management principle.

## Provenance

Standard senior care operations and census management practice; codifies the CLAUDE.md §3 #1 census-flow principle for the move-out retention side; grounded in senior housing and assisted-living consulting frameworks.

---

_Last reviewed: 2026-06-05 by `claude`_
