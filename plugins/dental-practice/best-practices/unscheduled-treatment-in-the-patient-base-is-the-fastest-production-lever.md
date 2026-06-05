# Unscheduled Treatment in the Patient Base Is the Fastest Production Lever

**Status:** Pattern
**Domain:** Practice growth / production
**Applies to:** `dental-practice`

---

## Why this exists

Most established dental practices have a significant pool of patients with treatment-planned but unscheduled work sitting in their practice management system — restorations, crowns, and other restorative procedures presented, accepted (or soft-declined), and never scheduled. This unscheduled treatment backlog represents the fastest production lever available: the patient has already been examined, treatment has already been recommended, there is no marketing cost, and the clinical relationship exists. Practices that do not systematically work this backlog leave production on the table while spending money on new-patient acquisition to fill the same gap.

## How to apply

Build a systematic unscheduled-treatment outreach workflow that runs on a quarterly cycle.

```
Unscheduled treatment workflow:
1. Pull the report (quarterly minimum):
   - Active patients (seen in 18 months) with open treatment plans > $200
   - Sort by: treatment value (highest first), last contact date
   - Tag: previously presented and accepted vs. not yet discussed

2. Segment by action type:
   - Accepted but not scheduled → appointment opportunity (highest priority)
   - Presented but declined → re-engagement needed
   - Not yet presented → add to next hygiene or recall appointment

3. Outreach script (accepted but not scheduled):
   "Hi [patient], this is [name] from [practice]. Dr. [X] wanted to follow up — 
   we have treatment on record for [procedure] that we haven't scheduled yet. 
   Do you have 5 minutes to find a time that works for you?"
   - Offer 2 specific appointment times, not open-ended availability
   - Document: contacted, outcome, next follow-up date

4. Metrics to track:
   - Total unscheduled treatment value by month
   - Conversion rate: contacted → scheduled
   - Production attributed to unscheduled treatment outreach each month
```

**Do:**
- Work the accepted-but-not-scheduled segment first — these have the highest conversion probability.
- Assign a specific team member (treatment coordinator or front-desk lead) ownership of the unscheduled-treatment report and outreach.
- Integrate unscheduled treatment review into each hygiene appointment — the hygienist is the natural re-presenter for open treatment during the recall visit.

**Don't:**
- Use a mass email blast as the primary outreach method for unscheduled treatment — a personal phone call converts at significantly higher rates.
- Attempt to re-present treatment that was explicitly declined more than twice without the dentist assessing whether the clinical situation has changed.
- Ignore the unscheduled treatment backlog in favor of new patient acquisition — the cost to convert an existing patient is a fraction of acquiring a new one.

## Edge cases / when the rule does NOT apply

Treatment plans older than 24 months should be clinically reviewed before outreach — the treatment need may have changed (condition worsened, tooth lost, patient's health changed). Re-present only after clinical re-evaluation.

## See also

- [`../agents/clinical-treatment-planner.md`](../agents/clinical-treatment-planner.md) — unscheduled treatment re-presentation is a case-acceptance conversation requiring the same sequencing principles.
- [`./case-acceptance-is-presentation-not-price.md`](./case-acceptance-is-presentation-not-price.md) — re-engaging unscheduled treatment requires the same communication approach as initial presentation.

## Provenance

Standard dental practice management and production strategy; codifies the treatment-planned-but-unscheduled lever widely cited in dental consulting practice (Jameson Management, Productive Dentist Academy, and similar frameworks).

---

_Last reviewed: 2026-06-05 by `claude`_
