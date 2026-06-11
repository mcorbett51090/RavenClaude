---
name: academic-program-viability-and-roi
description: "Evaluate academic programs on margin and mission together — establish market/labor demand, model contribution margin and breakeven enrollment, weigh the accreditation/general-education role, and frame launch / hold / restructure / sunset options with the swing assumptions."
---

# Academic Program Viability & ROI

**Purpose:** decide which programs to launch, keep, restructure, or sunset — judging each on
contribution margin *and* mission, never one alone.

---

## Steps

### 1. Establish demand (flag for verification)

For a new or struggling program, name the market/labor demand signal: job openings, wage data,
competitor offerings, applicant interest. Flag demand and wage figures as
`[unverified — confirm against current labor-market data]` per the Claim-Grounding protocol.

### 2. Model contribution margin, not gross tuition

```
program contribution = program tuition revenue − (direct instructional cost + program-specific cost)
```

Use [`../../scripts/higher_ed_calc.py`](../../scripts/higher_ed_calc.py) `program_contribution_margin`
and `breakeven_enrollment`. Gross tuition is meaningless until set against the cost to deliver it.

### 3. Weigh mission alongside margin

A program can be:

| Margin | Mission | Call |
|---|---|---|
| + | + | grow / protect |
| − | + (accreditation, gen-ed, strategic) | keep deliberately; fund from cross-subsidy |
| + | − (drift) | question / reposition |
| − | − | restructure or sunset |

The point is to make the keep-an-unprofitable-program decision **deliberate**, not accidental.

### 4. Read the portfolio for cross-subsidy

Lay out programs by contribution margin × enrollment trend. Identify which programs carry which, the
at-risk ones, and the mission-critical-but-unprofitable ones to protect on purpose.

### 5. Frame the options with swing assumptions

Launch/hold, restructure, sunset/teach-out — each with the assumption (enrollment, section size,
faculty load) that most changes the answer.

---

## Output

A program business case or viability analysis (margin + mission), a breakeven, and the options. Use
the [`program-viability-scorecard`](../../templates/program-viability-scorecard.md) template; deepen
with the [`budget-model-and-program-portfolio-reference`](../../knowledge/budget-model-and-program-portfolio-reference.md).
