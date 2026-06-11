---
description: "Model the admissions funnel and yield — instrument inquiry → enroll, find the leaking stage, segment by price/fit sensitivity, and tie every yield lever to net tuition revenue."
---

# /model-enrollment-funnel

Spawn `enrollment-and-financial-aid-strategist` to model the admissions funnel and build a yield plan.

## What it does

1. Instruments the funnel: `inquiry → applicant → admit → deposit → enroll → matriculated` (melt included).
2. Computes each stage's conversion via [`../scripts/higher_ed_calc.py`](../scripts/higher_ed_calc.py) and flags the steepest drop.
3. Segments by price- vs. fit-sensitivity and assigns the matching lever.
4. Ties each lever's effect to **net tuition revenue**, not gross.

## Usage

```
/model-enrollment-funnel
```

Then share your stage counts (or what you can instrument) and current discount rate. The agent
applies [`enrollment-funnel-and-yield`](../skills/enrollment-funnel-and-yield/SKILL.md) and uses the
[`enrollment-funnel-model`](../templates/enrollment-funnel-model.md) template.

## Good inputs

- Counts by funnel stage for one or more entering cohorts.
- Gross tuition and current institutional aid/discount rate (for the net-revenue math).
