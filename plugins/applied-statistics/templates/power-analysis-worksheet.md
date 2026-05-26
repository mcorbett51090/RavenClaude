# Power-analysis worksheet — <experiment name>

> Fill the four boxes; the fifth is computed. Do this **before** launch. See the
> [`power-and-sample-size`](../skills/power-and-sample-size/SKILL.md) skill.

| Input | Value | Notes |
|---|---|---|
| **α (significance)** | 0.05 | tolerated false-positive rate |
| **Power (1 − β)** | 0.80 | probability of detecting a true effect of the target size |
| **Baseline** | <current rate / mean> | from historical data |
| **MDE** | <smallest effect worth acting on> | business-meaningful, not just "statistically detectable" |
| **→ Required n (per group)** | <computed> | output |

## Computation (pick the one matching your outcome)

```python
# Continuous outcome (two-sample t): n per group
from statsmodels.stats.power import TTestIndPower
n = TTestIndPower().solve_power(effect_size=<d>, alpha=0.05, power=0.80, alternative="two-sided")

# Conversion / proportion: n per group for baseline p1 -> target p2
from statsmodels.stats.proportion import proportion_effectsize
from statsmodels.stats.power import NormalIndPower
es = proportion_effectsize(<p2>, <p1>)
n = NormalIndPower().solve_power(effect_size=es, alpha=0.05, power=0.80, alternative="two-sided")
```

## Feasibility check
- **Traffic available:** <units/day> → **time to reach n:** <days>
- If the required n is infeasible: raise the MDE (detect only bigger effects), accept lower power (state it), or don't run the test.

## If the sample is already fixed (invert it)
- Given n = <…>, the achievable **power** for the target MDE is <…>, or the **MDE** at 80% power is <…>.
- ⚠️ If power < 0.80, a null result is **not** "no effect" — report the CI and the detectable MDE (pitfall #8).
