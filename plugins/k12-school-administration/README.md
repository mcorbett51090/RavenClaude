# k12-school-administration

A **K-12 School Administration specialist team** for a principal, business manager, or district administrator accountable for enrollment, budget, and student outcomes. It manages enrollment as a funded pipeline not a headcount, reads attendance/ADA as both funding and an outcome signal, fits staffing ratios to the budget envelope, flags chronic absenteeism early, and reads outcomes segmented not school-average.

> Inherits the [`ravenclaude-core`](../ravenclaude-core/) protocols (claim-grounding, structured output, decision review). Level-explicit, organization-flexible (single school | district | charter network | public | independent).

## What you get

| Surface | Contents |
|---|---|
| **4 agents** | `school-administration-lead`, `enrollment-attendance-analyst`, `staffing-budget-specialist`, `student-outcomes-specialist` |
| **5 skills / commands** | `model-enrollment-funding` · `flag-chronic-absenteeism` · `fit-staffing-to-budget` · `allocate-per-pupil` · `read-outcomes-segmented` |
| **4-file knowledge bank** | KPI glossary · unit economics · 2025–2026 context · Mermaid decision trees |
| **4 templates** | scorecard · exec readout · enrollment-funding.md · staffing-budget.md |
| **1 advisory hook** | flags anti-patterns (unbaselined metric, unsourced benchmark, student PII (FERPA)) in generated deliverables |
| **`scripts/k12_school_administration_calc.py`** | stdlib calculator — `enrollment-funding` · `staffing-ratio` · `absenteeism` |

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install k12-school-administration@ravenclaude
```

## Quickstart

> "Enrollment is down and the budget is tight — what do we do?"

The `school-administration-lead` scopes the problem, routes to `enrollment-attendance-analyst` (or a sibling specialist), and synthesizes a ranked action plan with owners, dates, and expected metric movement.

## What it is not

a special-education legal/IEP authority, a FERPA compliance counsel, or a curriculum/pedagogy authority. It does not render IEP, FERPA, or student-discipline legal determinations, set curriculum, or store student PII. Special-ed law, FERPA, and student-rights questions route to counsel.
