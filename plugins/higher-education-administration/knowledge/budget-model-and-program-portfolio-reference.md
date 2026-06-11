# Budget model & program portfolio — reference

Deep reference for the `higher-ed-administration-lead` and `academic-program-portfolio-strategist`,
and the budget/program skills. Companion to [`higher-ed-decision-trees.md`](higher-ed-decision-trees.md).

---

## The tuition-dependent budget

```
tuition_dependency = net_tuition_revenue ÷ total_operating_revenue
```

A high dependency ratio means a small enrollment or discount miss flows straight to the operating
bottom line. Dependency itself isn't a failure — an unmanaged, unmodeled dependency is. Stress-test:
enrollment −5%/−10%, discount +3pts, melt spike → where does the budget break?

## Program contribution margin

```
program_contribution = program_tuition_revenue − (direct_instructional_cost + program_specific_cost)
breakeven_enrollment = fixed_program_cost ÷ contribution_per_student
```

Use [`../scripts/higher_ed_calc.py`](../scripts/higher_ed_calc.py) `program_contribution_margin` and
`breakeven_enrollment`. Gross tuition is meaningless until set against the cost to deliver.

## The margin × mission matrix

| Margin | Mission | Call |
|---|---|---|
| + | + | grow / protect |
| − | + | keep deliberately, fund from cross-subsidy |
| + | − | question / reposition (mission drift) |
| − | − | restructure or sunset / teach-out |

The discipline: every "keep an unprofitable program" decision is **deliberate and named**, not an
accident of inertia.

## Portfolio cross-subsidy

Lay programs out by contribution margin × enrollment trend. Surface:

- the programs that carry the institution (high margin),
- the at-risk ones (negative margin + declining enrollment),
- the mission-critical-but-unprofitable ones to protect on purpose,
- the quiet drains nobody decided to keep.

## Credit-hour economics

Section size × faculty load → credit-hour production → program contribution. Fill rate is the link
between course scheduling and the budget; chronic under-fill is both a scheduling and a margin problem.

## Governance framing

Present dependency, stress results, and portfolio risk as **risk with mitigations**, in board/CFO
language. A budget model that doesn't name the structural risk is a spreadsheet, not a decision.
