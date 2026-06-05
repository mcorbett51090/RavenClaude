# Acuity Reassessment Is a Revenue and Care Quality Event

**Status:** Absolute rule
**Domain:** Acuity pricing / clinical operations
**Applies to:** `senior-care-operations`

---

## Why this exists

Resident acuity changes continuously — it rarely stays flat after move-in. A resident who was low-acuity at move-in may develop dementia, fall risk, incontinence, or increased medication management needs within 6–12 months. When the care plan and acuity assessment are not updated to reflect these changes, two problems occur simultaneously: the community is providing more care than it is charging for (undercharging a high-acuity resident while recovering the base rate), and the care plan may not reflect the actual care being delivered (a survey and safety risk). Acuity reassessment is the mechanism that keeps the rate, the care plan, and the resident's actual condition aligned — it is both a revenue protection action and a clinical obligation.

## How to apply

Build acuity reassessment into the operations calendar as a scheduled event, triggered by both time and clinical change.

```
Acuity reassessment schedule:
Routine (time-based):
  - Move-in: comprehensive assessment at admission (required)
  - 90-day reassessment: first reassessment after admission
  - Semi-annual / annual thereafter: per state regulation and community policy

Triggered (event-based — reassess within 5 business days):
  - Hospitalization (any)
  - New diagnosis (especially dementia, Parkinson's, COPD, CHF, diabetes)
  - Fall with injury
  - Significant cognitive change (increased confusion, new wandering)
  - New incontinence or significant change in continence
  - New behavioral concern (agitation, refusal of care, elopement risk)
  - Weight loss >5% in 30 days or >10% in 6 months

Reassessment process:
  [ ] Nurse completes updated assessment using the community's acuity tool
  [ ] Current care needs compared to the current rate level
  [ ] If care needs have increased beyond the current level: rate adjustment letter to
      resident/responsible party per contract terms (minimum notice required varies by state)
  [ ] Care plan updated to reflect new acuity findings
  [ ] Documentation: assessment date, findings, rate change (if any), family notification

Revenue tracking:
  - Monthly: % of residents with reassessments current vs. due
    Target: 100% current (no overdue assessments)
  - Quarterly: revenue uplift from acuity rate adjustments vs. prior quarter
  - Annual: % of residents who have had at least one rate adjustment since move-in
    (a community with 0% annual rate adjustments in a 2+ year average LOS likely has
    undercharging or skipped reassessments)
```

**Do:**
- Notify the resident and/or responsible party of any rate increase in advance per the residence agreement terms — surprise rate increases produce move-outs and complaints.
- Document the clinical basis for the rate increase in the reassessment record — "increased care needs" is not sufficient; the specific findings must be documented.
- Review the reassessment schedule in the monthly clinical and financial review together — clinical staff and the finance lead must both see it.

**Don't:**
- Skip a triggered reassessment because "the resident is stable now" after a hospitalization — the return-from-hospital acuity is frequently higher than pre-hospitalization.
- Apply a blanket annual rate increase without an acuity basis — most senior care residence agreements require a care-based justification for rate increases above a standard inflationary adjustment.
- Allow the reassessment to occur without a corresponding care plan update — a reassessment that does not update the care plan is a documentation gap.

## Edge cases / when the rule does NOT apply

Independent living communities with no tiered care service fees do not have acuity-based rate adjustments, but should still conduct acuity monitoring to identify residents approaching a care level that requires transfer to assisted living.

## See also

- [`../agents/senior-care-finance-analyst.md`](../agents/senior-care-finance-analyst.md) — owns acuity pricing model and revenue analytics.
- [`../agents/clinical-care-compliance-specialist.md`](../agents/clinical-care-compliance-specialist.md) — owns the reassessment process and care plan compliance.
- [`./price-to-acuity-not-a-flat-rate.md`](./price-to-acuity-not-a-flat-rate.md) — the overarching pricing principle this rule operationalizes for ongoing residents.

## Provenance

Codifies CLAUDE.md §3 #2 (price to acuity) applied to the ongoing resident reassessment context; grounded in state ALF licensure regulations (which vary by state for reassessment frequency) and senior care operations consulting practice.

---

_Last reviewed: 2026-06-05 by `claude`_
