---
description: "Design a FERPA-aware early-alert system — choose leading risk signals, build a risk score, and define a tiered intervention ladder targeting the first-year cliff."
---

# /design-early-alert-system

Spawn `student-success-and-retention-analyst` (with the academic-operations coordinator for the data
flow) to design an early-alert system.

## What it does

1. Frames retention by entering cohort and locates the year-1→year-2 cliff.
2. Selects **leading** risk signals (attendance, LMS engagement, midterm/gateway grades, financial holds).
3. Builds a risk score via [`../scripts/higher_ed_calc.py`](../scripts/higher_ed_calc.py) `early_alert_score`.
4. Defines the tiered intervention ladder (watch / elevated / high).
5. Designs the data flow **FERPA-aware** — access scoped to legitimate educational interest.

## Usage

```
/design-early-alert-system
```

Then describe the signals you can collect and who would act on alerts. The agent applies
[`student-retention-and-early-alert`](../skills/student-retention-and-early-alert/SKILL.md) and the
[`early-alert-playbook`](../templates/early-alert-playbook.md) template.

## Good inputs

- Which leading signals are available in your SIS/LMS.
- The advising/intervention roles who would own each tier.
