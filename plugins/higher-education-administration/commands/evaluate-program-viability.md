---
description: "Evaluate an academic program on margin and mission — establish demand, model contribution margin and breakeven enrollment, weigh the accreditation/gen-ed role, and frame launch / hold / restructure / sunset options."
---

# /evaluate-program-viability

Spawn `academic-program-portfolio-strategist` to build a program business case or viability analysis.

## What it does

1. Establishes market/labor demand (flagged for verification).
2. Models contribution margin and breakeven enrollment via [`../scripts/higher_ed_calc.py`](../scripts/higher_ed_calc.py).
3. Weighs the mission role (accreditation, general-education, strategic fit) alongside margin.
4. Frames launch / hold / restructure / sunset options with the swing assumptions.

## Usage

```
/evaluate-program-viability
```

Then share the program, enrollment, tuition, and instructional/program costs. The agent applies
[`academic-program-viability-and-roi`](../skills/academic-program-viability-and-roi/SKILL.md) and the
[`program-viability-scorecard`](../templates/program-viability-scorecard.md) template.

## Good inputs

- Program tuition revenue and direct instructional + program-specific costs.
- Enrollment trend and any mission/accreditation role the program plays.
