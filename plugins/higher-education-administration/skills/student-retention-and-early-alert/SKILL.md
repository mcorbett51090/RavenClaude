---
name: student-retention-and-early-alert
description: "Diagnose retention by cohort and design an early-alert system — frame persistence by entering cohort, target the first-year cliff, build a leading-signal risk score, and define a tiered intervention ladder that is FERPA-aware by design."
---

# Student Retention & Early Alert

**Purpose:** lift persistence and completion by measuring retention as a cohort phenomenon, catching
risk with leading signals, and intervening on a tiered ladder — all built FERPA-aware.

---

## Steps

### 1. Frame retention by entering cohort

Never report a point-in-time headcount as "retention." Track each entering cohort's persistence:
year-1→year-2, year-2→year-3, through to completion. Use
[`../../scripts/higher_ed_calc.py`](../../scripts/higher_ed_calc.py) `retention_rate`.

### 2. Target the first-year cliff

Most attrition concentrates between year one and year two. Segment the year-1→year-2 drop by entering
characteristics (academic preparation, first-gen, financial need, residential vs. commuter) to find
the highest-attrition group.

### 3. Build a leading-signal risk score

Lagging signals (a failed semester) arrive too late. Score risk on leading signals:

| Signal | Why it leads |
|---|---|
| Attendance / early no-shows | Disengagement precedes withdrawal |
| LMS engagement drop | Behavioral early warning |
| Midterm / gateway-course grades | Academic struggle, still recoverable |
| Financial holds / aid gaps | A solvable barrier, if caught early |

Use `early_alert_score` to combine signals into a tiered risk level.

### 4. Define the tiered intervention ladder

| Risk tier | Trigger | Intervention |
|---|---|---|
| Watch | 1 signal | Automated nudge, advisor visibility |
| Elevated | 2 signals | Proactive advisor outreach |
| High | 3+ / financial hold | Case-managed intervention, wraparound support |

### 5. Build it FERPA-aware

Define who has a legitimate educational interest in each signal before building the dashboard.
Coordinate the data flow with the academic-operations-and-compliance coordinator. FERPA is a design
input, not a later review.

---

## Output

A cohort persistence analysis, an early-alert risk-score design, and a tiered intervention ladder.
Use the [`../../templates/early-alert-playbook.md`](../../templates/early-alert-playbook.md) template.
