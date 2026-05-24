---
name: success-plan-authoring
description: Author a 30/60/90 day or quarterly success plan for an EdTech partner that has measurable success criteria, named owners, and a defensible cadence. Reach for this skill when onboarding a new partner OR when refreshing a quarterly plan after a renewal / midyear review.
---

# Skill: Success Plan Authoring

A success plan that says "the partner will be happier" doesn't survive contact with reality. This skill produces a success plan that the partner and the PSM both consult, that has measurable success criteria, and that catches its own failure modes early.

## Step 1 — Anchor on the partner's stated goals (in their words)

Pull from the partner profile (curated by `partner-profile-curator`). Use the partner's verbatim language. If the profile doesn't have the partner's stated goals yet, **stop and capture them first** — a success plan against goals you assumed is worse than no plan.

Examples of partner-stated goals (verbatim, attributed):
- *"We want our teachers to spend less time grading and more on small-group instruction"* — Jane Smith, Curriculum Director, 2026-03-12
- *"Our biggest risk is staff turnover; whatever we adopt has to survive next year's classroom changes"* — Mike Lee, Superintendent, 2026-02-04

## Step 2 — Translate goals to measurable outcomes (this is the hard part)

For each partner-stated goal, name **one observable outcome** that would prove the goal was met. The outcome must be:

- **Measurable** — a number, a rate, a count, a categorical fact (not "a feeling")
- **Attributable** — the partner and the PSM both agree the product moved this outcome (or at least contributed materially)
- **Time-boxed** — observed by date X
- **Defensible** — the source query / measurement method is documented; the partner could audit it

Example translation:
- Goal: *"teachers spend less time grading"*
- Outcome: median teacher self-reported grading time drops from baseline X (measured pre-launch) to Y by end-of-quarter, per the monthly teacher survey (instrumented in the LMS)

**Anti-pattern:** outcomes that are easy to measure but don't actually answer the goal. "Logins are up" doesn't prove teachers spend less time grading.

## Step 3 — Sequence into 30 / 60 / 90 (or quarterly milestones)

A 30/60/90 is **not** "do everything in the first 30 days." Sequence by dependency:

- **30 days** — onboarding complete; baseline measurements captured; named champion engaged; first small win identified
- **60 days** — adoption depth crosses an instrumented threshold; mid-cycle check-in completed; rostering / SIS / LMS data quality validated; first measurable outcome trend visible
- **90 days** — first measurable outcome assessed against target; refresh decision (continue / adjust / escalate); QBR ready

Each milestone has:
- A specific measurable check (the same kind as in Step 2)
- A named owner *on our side* and *on the partner's side*
- A date (not "during week 6"; an actual date)

## Step 4 — Cadence

How often is the PSM in touch, in what channel, with what content? Defaults vary by segment:

- **K-12 (district / school):** every 2 weeks during the school year; pause / async during summer; high-frequency during fall start-of-year (first 4 weeks); QBR cadence aligned to academic quarters, **not** calendar quarters
- **Higher-ed (institution / department):** every 3 weeks during the academic term; reduced during break and finals; QBR aligned to the institution's academic + fiscal calendar (which are often different)
- **Corporate L&D:** every 2 weeks during active cohort; reduced between cohorts; QBR aligned to the partner's fiscal quarter

Cadence is **segment-aware in the plan**, not assumed.

## Step 5 — Risks and red-flag triggers (the part most plans skip)

For each milestone, name the 2 things most likely to go wrong. Examples:

- **30-day risk:** rostering data hasn't synced cleanly → milestone slips into 60-day window
- **60-day risk:** named champion leaves the role → recovery play fires; refresh the champion-redundancy section of the profile
- **90-day risk:** measured outcome misses target → refresh decision: was the target wrong, the cadence wrong, or the product wrong? Different answer drives different action.

These risks should be **trigger-mapped to recovery plays** (`success-playbook-designer` owns the play library).

## Step 6 — Document the decision rules

A success plan has decision points. Make them explicit:

- "If outcome X is below target by 20% at 60 days, escalate to leadership for a refresh conversation"
- "If champion engagement drops below 1 meaningful touchpoint per month for 2 consecutive months, fire the recovery play"
- "If rostering data quality issues persist past 30 days, escalate to product"

A success plan without decision rules is a wish list.

## Step 7 — Get partner sign-off in writing

The plan exists only when the partner agrees with it in writing. A verbal "sounds good" is a churn vector at the next leadership change. Capture:

- Partner-side signer (named role, named person)
- Date of agreement
- The specific measurable outcomes agreed to (so a successor on either side can't claim "that's not what we agreed")
- Refresh cadence (quarterly is the default)

## What this skill does NOT cover

- Health-score design (route to `partner-health-scoring`)
- QBR composition (route to `qbr-composition`)
- Play design when a risk fires (route to `success-playbook-designer`)
- Comms variants of the plan for partner-side audiences (route to `ferpa-comms-translator`)
- Generic project-plan templating (route to `ravenclaude-core/project-manager`)
