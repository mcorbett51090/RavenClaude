# Check for Simpson's paradox when an aggregate trend conflicts with subgroup trends

**Status:** Primary diagnostic
**Domain:** Data analysis / confounding
**Applies to:** `applied-statistics`

---

## Why this exists

Simpson's paradox occurs when a trend present in aggregate data reverses or disappears when the data is stratified by a third variable. The classic example: Treatment A outperforms Treatment B in aggregate, but Treatment B outperforms Treatment A in every individual subgroup — because more sick patients were assigned to Treatment A. In business analytics, it appears as "our overall conversion rate improved" but "conversion improved in no individual country." The aggregate number is not wrong, but it is misleading without the subgroup context. Any time an aggregate metric and subgroup metrics appear to conflict, check for Simpson's before reporting the aggregate.

## How to apply

```python
import pandas as pd

def check_simpsons(df, outcome_col, treatment_col, stratum_col):
    """
    Checks whether the aggregate treatment effect direction
    is consistent across all strata.
    Returns a flag if the aggregate and any stratum disagree.
    """
    agg_rate = df.groupby(treatment_col)[outcome_col].mean()
    agg_direction = agg_rate.iloc[1] > agg_rate.iloc[0]  # True if group 1 > group 0

    stratum_directions = []
    for stratum, sub_df in df.groupby(stratum_col):
        rates = sub_df.groupby(treatment_col)[outcome_col].mean()
        if len(rates) == 2:
            stratum_directions.append(rates.iloc[1] > rates.iloc[0])

    conflict = any(d != agg_direction for d in stratum_directions)
    if conflict:
        print(f"WARNING: Simpson's paradox detected. Aggregate direction "
              f"({'higher' if agg_direction else 'lower'}) conflicts with "
              f"{sum(d != agg_direction for d in stratum_directions)} strata.")
    return conflict

# Usage
check_simpsons(df, outcome_col='converted', treatment_col='variant', stratum_col='country')
```

**Diagnostic checklist (run when aggregate conflicts with segment):**

1. Identify the suspected confounding variable (the stratification variable).
2. Compare aggregate effect to stratum-specific effects.
3. Check whether the confound is also associated with treatment assignment.
4. If Simpson's is confirmed: report the stratum-specific effects as the primary result; the aggregate is misleading.

**Do:**
- Run the stratum check whenever an aggregate result is being reported alongside segment breakdowns.
- Report the confounding variable explicitly when Simpson's is detected.
- Use the stratum-specific effects as the primary result when the confound is relevant.

**Don't:**
- Report only the aggregate when subgroup analysis was run and a conflict was found.
- Dismiss Simpson's as an "edge case" — it appears regularly in marketing and clinical data.

## Edge cases / when the rule does NOT apply

- When there is no third variable stratification (a single-group aggregate with no subgroups), there is nothing to conflict and the check is not applicable.

## See also

- [`../agents/applied-statistician.md`](../agents/applied-statistician.md) — screens for this as part of the experiment-analysis skill
- [`./causal-watch-confounders-and-colliders.md`](./causal-watch-confounders-and-colliders.md) — the confounding rule that Simpson's paradox is a special case of

## Provenance

Simpson's paradox (Simpson, 1951; Yule, 1903 for the earlier version). Codifies applied-statistics CLAUDE.md §4 anti-patterns (the experiment-analysis skill's "Simpson's screen"). Standard diagnostic in the experiment-analysis skill and the pitfall guardrail knowledge files.

---

_Last reviewed: 2026-06-05 by `claude`_
