---
scenario_id: 2026-06-05-enrollment-shortfall-recovery
contributed_at: 2026-06-05
plugin: clinical-trials
product: recruitment
product_version: "n/a"
scope: likely-general
tags: [enrollment, recruitment-funnel, rescue, eligibility, site-activation]
confidence: medium
reviewed: false
---

## Problem

A Phase II trial was four months into enrollment and tracking at ~40% of its randomization plan. The sponsor's instinct was the classic enrollment-rescue reflex: **add more sites**. The CRO had quoted a 12-site expansion. The ask was to confirm the diagnosis before committing the capital — because adding sites to a trial whose *real* constraint is upstream just buys a second set of under-enrolling sites at full activation cost.

## Context

- Segment: Phase II, single therapeutic indication, ~25 active sites, US + EU mix.
- Constraint: this is a **recruitment-funnel** problem, and the team was reading a raw enrolled *count* instead of the funnel rate (CLAUDE.md §3 #5 — enrollment is a rate, not a count). Without screened → screen-failed → enrolled → retained, you can't tell whether the leak is referral volume, eligibility, or consent.
- The plugin is **not** an EDC/CTMS and makes no eligibility determinations — it framed the funnel read and the costed options as decision-support for the sponsor's clinical-ops lead (CLAUDE.md §2).

## Attempts

- Tried: pulled the **funnel by site**, not the aggregate count. Found two distinct failure modes hiding under one "we're behind" headline: (a) a cluster of sites with **healthy screening but a high screen-fail rate** (an eligibility-criteria problem) and (b) a cluster that was **barely screening at all** (a referral / site-engagement problem). Outcome: ruled out the single-cause "we need more sites" story — the leak was upstream and bifurcated.
- Tried: grounded the severity against public benchmarks rather than memory — the failure pattern is industry-endemic, not a one-trial anomaly: roughly **68% of sites fail to meet their projected enrollment targets**, about **one-third of sites enroll zero or one patient**, and an estimated **80–85% of trials miss their initial enrollment targets** [verify-at-use]. Outcome: reframed the problem as "fix the funnel before you scale it," not "this trial is uniquely broken."
- Tried (the move that worked): sequenced **fix-before-scale**. For the high-screen-fail cluster, flagged the two or three most-restrictive eligibility criteria for a protocol-amendment feasibility review (restrictive criteria are the single biggest enrollment killer — CLAUDE.md §3 #1); for the low-screening cluster, costed a targeted referral/engagement intervention against the per-patient economics (~**$6,533** to recruit a patient [verify-at-use]) rather than a blanket site add. Site expansion was deferred to a *fallback*, not the first move. Outcome: a costed, staged recovery plan with a per-stage funnel target instead of a $X00k site-expansion reflex.

## Resolution

The shortfall was **two upstream funnel leaks** (eligibility on one cluster, referral volume on another), not a site-count shortage. Reading the funnel by site separated the two; benchmarking confirmed the pattern is endemic, not unique; and the recovery sequenced the cheap, fast levers (criteria review + targeted referral) ahead of the expensive, slow one (site activation — the schedule's long pole, CLAUDE.md §3 #4).

**Action for the next consultant hitting this pattern:** when a trial is "behind," **read the funnel by site before you cost a site add.** Separate screen-fail (eligibility) from low-screening (referral) — they need opposite fixes. Benchmark the gap so the sponsor knows whether it's an outlier or the industry norm. Only after the upstream leak is addressed does adding sites stop being throwing activation cost at a leak. Cross-reference [`../knowledge/trials-enrollment-shortfall-recovery-decision-tree.md`](../knowledge/trials-enrollment-shortfall-recovery-decision-tree.md) and the [`../skills/plan-recruitment-funnel/SKILL.md`](../skills/plan-recruitment-funnel/SKILL.md) playbook. The [`../scripts/trials_calc.py`](../scripts/trials_calc.py) `enrollment-feasibility` mode does the sites × rate × months arithmetic.

**Sources (retrieved 2026-06-05):**
- Applied Clinical Trials — *The Enrollment Rescue Dilemma*: https://www.appliedclinicaltrialsonline.com/view/enrollment-rescue-dilemma-how-sponsors-and-sites-can-make-most-tough-situation
- WCG — *Avoid Enrollment Pitfalls: Find Your Best-fit Clinical Trial Sites* (site-level under-enrollment figures): https://www.wcgclinical.com/wp-content/uploads/2022/03/avoid-enrollment-pitfalls-best-clinical-trial-sites.pdf
- Sofpromed — *The Ultimate Guide to Clinical Trial Costs* (per-patient recruitment cost): https://www.sofpromed.com/ultimate-guide-clinical-trial-costs

Site-performance and cost figures vary by phase and therapeutic area — treat as `[verify-at-use]` and validate against the trial's own EDC/CTMS funnel data before any deliverable (CLAUDE.md §3 #8).
