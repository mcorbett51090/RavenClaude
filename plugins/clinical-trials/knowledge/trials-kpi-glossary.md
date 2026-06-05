# Clinical trial KPI glossary

The operational metrics a trial is judged on — formulas, the misreads, and where a benchmark needs a date. Every external figure carries a source + retrieval date or an `[unverified — training knowledge]` / `[ESTIMATE]` mark (CLAUDE.md §3 #8). These are decision-support definitions, not regulatory or statistical determinations (CLAUDE.md §2).

## Enrollment metrics

| Metric | Formula / definition | The misread it prevents |
|---|---|---|
| **Screening rate** | patients screened / site / month | A raw enrolled count hides whether the leak is referral volume vs eligibility (§3 #5). |
| **Screen-fail rate** | screen-failed / screened | A high screen-fail rate is an **eligibility-criteria** signal, not a recruitment-volume one — opposite fix. |
| **Screen-to-enroll ratio** | screened / enrolled | Tells you how many you must screen to hit the enrolled target; rises as criteria tighten. |
| **Enrollment rate vs plan** | actual randomized / planned randomized, by period | "We're behind" is meaningless without the per-period plan and the per-site breakdown. |
| **Sites enrolling zero / one** | count of sites at 0 or 1 randomization | The classic under-enrollment signature — see benchmarks below. |

**Benchmark (industry aggregates, `[verify-at-use]`):** ~**68%** of sites fail to meet projected enrollment targets; ~**one-third** of sites enroll **zero or one** patient; an estimated **80–85%** of trials miss their **initial** enrollment target. Sources: WCG, *Avoid Enrollment Pitfalls* (https://www.wcgclinical.com/wp-content/uploads/2022/03/avoid-enrollment-pitfalls-best-clinical-trial-sites.pdf); Applied Clinical Trials, *The Enrollment Rescue Dilemma* (https://www.appliedclinicaltrialsonline.com/view/enrollment-rescue-dilemma-how-sponsors-and-sites-can-make-most-tough-situation). Retrieved 2026-06-05. Figures vary by phase/indication — calibrate to the trial's segment.

## Retention & cost metrics

| Metric | Definition | Benchmark (`[verify-at-use]`) |
|---|---|---|
| **Dropout / attrition rate** | patients lost / enrolled | Average **~30%** [verify-at-use] |
| **Per-patient cost** | total trial cost / randomized patients | **~$113,000–$136,000** [verify-at-use] |
| **Cost to recruit a patient** | recruitment spend / enrolled | **~$6,533** [verify-at-use] |
| **Cost to replace a lost patient** | re-recruitment + lost-data cost / replacement | **~$19,533** [verify-at-use] — replacement ≫ recruitment, so retention pays (§3 #3) |
| **Recruitment + retention as % of budget** | (recruitment + retention spend) / total | **~20–30%** of trial budget [verify-at-use] |

Sources: Sofpromed, *The Ultimate Guide to Clinical Trial Costs* (https://www.sofpromed.com/ultimate-guide-clinical-trial-costs); mdgroup, *The True Cost of Patient Drop-outs* (https://mdgroup.com/blog/the-true-cost-of-patient-drop-outs-in-clinical-trials/). Retrieved 2026-06-04/05. (See [`trials-benchmarks-2026.md`](trials-benchmarks-2026.md) for the full cost breakdown by category.)

## Schedule metrics

| Metric | Definition | The misread it prevents |
|---|---|---|
| **Site-activation cycle time** | selection → contracting → green-light, per site | Activation is the schedule's long pole (§3 #4); a slow site is a start-up problem, not a recruitment one. |
| **First-patient-in (FPI)** | date first patient randomized | A slipping FPI is almost always an activation/start-up slip, caught early. |
| **Last-patient-in (LPI)** | date last patient randomized | Gates database lock and the submission timeline downstream. |
| **Delay rate** | trials delayed ≥ 1 month | ~**80%** of trials delayed ≥ a month; delay costs ~**$0.6M–$8M/day** in lost opportunity [verify-at-use] (§3 #4). |

## Quality & monitoring metrics

| Metric | Definition | The misread it prevents |
|---|---|---|
| **Protocol-deviation rate** | important deviations / site (or / patient) | Reading deviations one-by-one hides the **pattern** (cluster + root cause) a CAPA needs. |
| **Query rate / resolution time** | open queries per CRF; days-to-close | The centralized-monitoring signal that flags an outlier site for a targeted on-site visit. |
| **SDV coverage** | % of source data verified on-site | Under ICH E6(R3), 100% SDV is the wrong default — SDV touches ~**1%** of CRF data, ~**2.4%** of critical-data queries, while consuming ~**25–40%** of trial cost [verify-at-use]. Set SDV by **data criticality** (see [`trials-monitoring-intensity-decision-tree.md`](trials-monitoring-intensity-decision-tree.md)). |
| **CAPA effectiveness** | recurrence of the deviation after the CAPA, over a window | "Re-trained" with no dated, measurable effectiveness check is a note, not a CAPA. |

Source for SDV figures: Applied Clinical Trials, *Risk-Based Monitoring Versus Source Data Verification* (https://www.appliedclinicaltrialsonline.com/view/risk-based-monitoring-versus-source-data-verification), retrieved 2026-06-05.

## Submission-readiness metrics

| Metric | Definition | The misread it prevents |
|---|---|---|
| **Documentation completeness** | required submission docs assembled / total | The submission is built **throughout**, not at the end (§3 #7) — a final-month inventory is a delay waiting to happen. |
| **eCTD structure validation** | technical validation pass on the eCTD | A structural gap surfaces late and is expensive to fix under timeline pressure. |
| **IND 30-day window** | calendar days post-submission before trial start | The sponsor must wait **30 calendar days**; advertising, screening, and consent are **prohibited** during the hold [verify-at-use]. Source: FDA IND application (https://www.fda.gov/drugs/types-applications/investigational-new-drug-ind-application), retrieved 2026-06-05. |

## Sourcing note

Benchmark figures are industry aggregates that vary widely by phase and therapeutic area, and several (regulatory windows, SDV statistics) are volatile. Each carries a source URL + retrieval date or an inline `[verify-at-use]` / `[unverified — training knowledge]` mark. Validate against a primary source and the trial's own data before putting any figure in a client deliverable (§3 cite-or-mark rule). The runnable [`../scripts/trials_calc.py`](../scripts/trials_calc.py) computes the enrollment-feasibility, recruitment-funnel, and retention-ROI arithmetic from inputs you supply — it is a calculator, not a benchmark source.
