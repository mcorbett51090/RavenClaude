---
name: budget-model-and-tuition-dependency
description: "Model the institutional budget and its tuition dependency — link net tuition revenue to the operating budget, measure reliance on tuition vs. other revenue, stress-test enrollment/discount scenarios, and surface the structural risk before it becomes a crisis."
---

# Budget Model & Tuition Dependency

**Purpose:** connect enrollment and net tuition revenue to the operating budget, and quantify how
exposed the institution is to an enrollment or discount-rate shock.

---

## Steps

### 1. Build the revenue base

Lay out the revenue lines: net tuition revenue, auxiliary, endowment draw, grants/contracts,
state/appropriations, gifts. Use [`../../scripts/higher_ed_calc.py`](../../scripts/higher_ed_calc.py)
`net_tuition_revenue` for the tuition line — gross minus institutional aid, never sticker price.

### 2. Measure tuition dependency

```
tuition_dependency = net_tuition_revenue ÷ total_operating_revenue
```

Use `tuition_dependency_ratio`. A high ratio means a small enrollment or discount miss flows straight
to the bottom line. Dependency is not inherently bad — but it must be a *known, managed* risk.

### 3. Stress-test the scenarios

Model the budget under: enrollment −5%/−10%, discount rate +3pts, a melt spike. Show where each
scenario breaks the budget. The goal is to find the cliff before you're standing on it.

### 4. Connect to the levers

Tie the stress results back to the actionable levers: retention (protects multi-year net revenue),
yield (non-aid first), program portfolio (cross-subsidy), and cost structure. The budget model is
where the retention-vs-recruitment and discount-rate decisions get their dollar weight.

### 5. Frame for governance

Present the dependency and the stress results as risk, with the mitigations — in the language a board
and CFO share. A budget model that doesn't name the structural risk is a spreadsheet, not a decision.

---

## Output

A budget model with the tuition-dependency ratio, the stress-test results, and the mitigations tied
to levers. Deepen with the
[`budget-model-and-program-portfolio-reference`](../../knowledge/budget-model-and-program-portfolio-reference.md).
