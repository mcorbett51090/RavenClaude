---
name: staffing-scorecard-build
description: Build a staffing operations scorecard where every KPI carries a definition, formula, window, baseline, owner, drill-down, and a triggered action — so an operator can act on it Monday morning. Reach for this when standing up a new scorecard or auditing one that reports numbers nobody acts on.
---

# Skill: Build a staffing operations scorecard

A scorecard is useful when it changes what an operator does. A number with no definition, no comparison, and no triggered action is decoration. This skill keeps it honest.

## Step 1 — Pick the decision the scorecard serves
Name the one question it answers: "are we filling fast enough to win placements?", "is margin holding?", "is the desk the right size?" A scorecard that tries to answer everything answers nothing. Everything below flows from this.

## Step 2 — Choose 5–9 KPIs, by family (more is noise)
Pull from [`../../knowledge/staffing-kpi-glossary.md`](../../knowledge/staffing-kpi-glossary.md). A balanced operations scorecard usually spans:
- **Demand/funnel:** fill rate (name the denominator), time-to-fill (to *start*, incl. credentialing), requisition aging.
- **Speed:** time-to-submit/present (speed wins the placement).
- **Financial:** gross margin (bill−pay−burden), DSO.
- **Quality/retention:** redeployment rate, fall-off rate, client/candidate NPS.
- **Productivity:** hires/recruiter normalized for reqs-per-recruiter.

## Step 3 — For each KPI, fill the seven fields (no field, no ship)
| Field | Rule |
|---|---|
| Definition | The exact denominator/numerator; resolve the fill-rate ambiguity here |
| Formula | Written out, so two people compute it the same way |
| Window | Trailing 30/90/etc.; must not straddle a seasonal boundary (§3 #5) |
| Baseline | Prior period / SLA / cohort / target — the thing it's measured *against* (§3 #1) |
| Owner | A named role accountable for the number |
| Drill-down | The 2–3 components behind it (so a red number explains itself) |
| Triggered action | What the owner does at each band (green/yellow/red) |

## Step 4 — Pair the metrics
Place fill rate and time-to-fill adjacent; margin with its bill/pay/burden drill-down; revenue-per-recruiter with reqs-per-recruiter. A lone number on a scorecard invites the wrong fix (§3 #2, #3, #4).

## Step 5 — Segment the view
Healthcare-travel, locum, allied, per-diem, education-school-based don't share benchmarks or seasonality. Either filter by segment or show them side-by-side — never blend them into one average.

## Step 6 — Set the bands and the actions
Green/yellow/red thresholds tied to the baseline, each with the action it triggers. If the owner has to compute anything mentally to know what to do, redesign it.

## Step 7 — Mark the soft numbers
Any benchmark from an advisory blog is `[ESTIMATE]`; any figure not read first-hand is `[unverified]`. The client's own data is the baseline; external benchmarks are context (§3 #9).

## Output
Use [`../../templates/kpi-scorecard.md`](../../templates/kpi-scorecard.md). Demo data shape: [`../../bi-report/data.json`](../../bi-report/data.json). For the dashboard *layout*, route to [`kpi-dashboard-design`](../kpi-dashboard-design/SKILL.md); for instrumentation/build, to `ravenclaude-core/data-engineer`.

## What this skill does NOT cover
- Diagnosing *why* a KPI moved → [`fill-rate-diagnostics`](../fill-rate-diagnostics/SKILL.md), [`bill-rate-margin-modeling`](../bill-rate-margin-modeling/SKILL.md).
- Building the dashboard UI → `ravenclaude-core/data-engineer`.
