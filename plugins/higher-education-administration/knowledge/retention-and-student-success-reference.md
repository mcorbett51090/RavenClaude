# Retention & student success — reference

Deep reference for the `student-success-and-retention-analyst` and the retention/early-alert skill.
Companion to [`higher-ed-decision-trees.md`](higher-ed-decision-trees.md).

---

## Cohort framing (non-negotiable)

Retention, persistence, and completion are cohort phenomena. Track each entering cohort:
year-1→year-2, year-2→year-3, … → completion (e.g., 4-/6-year graduation rate). A point-in-time
headcount can hold steady while a cohort hemorrhages — only cohort framing reveals it.

## The year-1 → year-2 cliff

Most attrition concentrates at the first-to-second-year transition, where belonging, academic
momentum, and financial fit are still malleable. A student who reaches year two is far more likely to
complete. Interventions here protect the entire remaining enrollment; later-year interventions touch a
smaller, self-selected population.

## Leading vs. lagging signals

| Leading (act on these) | Lagging (too late) |
|---|---|
| Attendance / early no-shows | failed semester |
| LMS engagement drop | term GPA below threshold |
| Midterm / gateway-course grade | end-of-year withdrawal |
| Financial hold / aid gap | non-return at census |

An early-alert system built on lagging signals fires after the loss. Score leading signals.

## Early-alert risk tiers and the intervention ladder

| Tier | Trigger | Intervention |
|---|---|---|
| Watch | 1 signal | automated nudge, advisor visibility |
| Elevated | 2 signals | proactive advisor outreach |
| High | 3+ / financial hold | case-managed, wraparound support |

Use [`../scripts/higher_ed_calc.py`](../scripts/higher_ed_calc.py) `early_alert_score`.

## Segmenting the attrition

Decompose the year-1→year-2 drop by entering characteristics (academic preparation, first-gen,
financial need, residential vs. commuter) to find the highest-attrition group and target the driver:

| Concentration | Lever |
|---|---|
| Underprepared | gateway-course support, tutoring |
| First-gen / belonging | advising, belonging interventions |
| Financial need / holds | aid-gap intervention, hold resolution |
| Diffuse | first-year-experience redesign |

## FERPA reminder

Early-alert data is student education-record data. Design access around legitimate educational
interest **before** building; coordinate the data flow with academic operations & compliance.
