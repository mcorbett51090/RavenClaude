---
name: institutional-research-and-ipeds-reporting
description: "Produce trustworthy institutional numbers — pin canonical data definitions (census date, headcount vs. FTE, cohort rules), construct IPEDS/mandated cohorts correctly, spec FERPA-aware dashboards, and pressure-test predictive models before anyone acts on them."
---

# Institutional Research & IPEDS Reporting

**Purpose:** make the institution's numbers right, consistent, and defined — the data layer beneath
every enrollment, retention, and program decision.

> **Compliance note:** IPEDS and mandated-reporting definitions change. Treat specifics below as
> `[verify against current IPEDS/accreditor definitions]`.

---

## Steps

### 1. Pin the canonical definitions first

Before any number is reported, settle:

| Definition | Why it must be fixed |
|---|---|
| Census date | "Enrollment" differs by the day you count |
| Headcount vs. FTE | Two legitimate numbers; never interchangeable |
| Cohort inclusion rules | Full-time first-time? transfers? part-time? |
| Source of truth | The one system whose number is official |

Disagreeing offices are almost always a definitions problem, not a data problem.

### 2. Construct cohorts correctly

For IPEDS graduation-rate reporting, build the entering full-time first-time cohort with the correct
exclusions and the 150%-time completion window. Document the methodology so it's reproducible and
comparable year over year. Use [`../../scripts/higher_ed_calc.py`](../../scripts/higher_ed_calc.py)
`retention_rate` / graduation math.

### 3. Spec dashboards decision-makers trust

Each dashboard metric carries its definition, cohort framing, official source, and refresh cadence.
Build access FERPA-aware (legitimate educational interest). A dashboard whose numbers can't be traced
to a definition will be argued with instead of acted on.

### 4. Pressure-test predictive models before acting

| Check | Failure it catches |
|---|---|
| Target definition | "predicting" something circular |
| Leakage | a feature that encodes the outcome |
| Leading vs. lagging | a model that fires too late to act |
| Base rate / calibration | confident-but-wrong probabilities |
| Decision threshold | a score nobody can act on |

A model that leaks the outcome is worse than none.

---

## Output

A data-definitions standard, a documented cohort method, a dashboard spec, or a model review. Deepen
with the [`compliance-and-accreditation-reference`](../../knowledge/compliance-and-accreditation-reference.md).
