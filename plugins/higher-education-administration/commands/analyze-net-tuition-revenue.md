---
description: "Analyze net tuition revenue across discount scenarios — compute gross-to-net and discount rate, find the diminishing-returns point, and recommend a segmented aid-leveraging strategy."
---

# /analyze-net-tuition-revenue

Spawn `enrollment-and-financial-aid-strategist` (with `higher-ed-administration-lead` for the budget
envelope) to analyze net tuition revenue and the discount rate.

## What it does

1. Computes net tuition revenue and discount rate via [`../scripts/higher_ed_calc.py`](../scripts/higher_ed_calc.py).
2. Models net revenue across discount scenarios and finds the **diminishing-returns point**.
3. Separates need-based access aid from merit/leveraging aid.
4. Recommends a segmented leveraging strategy (price- vs. fit-sensitive admits) with Title IV points flagged for verification.

## Usage

```
/analyze-net-tuition-revenue
```

Then share gross tuition, current discount rate, and class size. The agent applies
[`financial-aid-and-net-revenue`](../skills/financial-aid-and-net-revenue/SKILL.md).

## Good inputs

- Gross tuition, current institutional aid spend, enrolled headcount.
- Yield by aid band if available (to find the diminishing-returns point).
