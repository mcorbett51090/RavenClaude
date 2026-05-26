---
name: power-and-sample-size
description: Compute or advise the sample size an experiment needs BEFORE it launches — from α (0.05), power (0.80), and a minimum detectable effect (MDE) — or compute the power/MDE a fixed sample can achieve. Prevents the underpowered-study pitfall and is the prerequisite to any A/B test. Returns the n, the assumptions behind it, and a runnable snippet. Used by `applied-statistician` (primary).
---

# Skill: power-and-sample-size

> **Invoked by:** `applied-statistician` (primary). Prerequisite for [`../experiment-analysis/SKILL.md`](../experiment-analysis/SKILL.md) — no experiment ships without it.
>
> **When to invoke:** "how big a sample do I need?"; "is this test big enough to trust a null result?"; planning any A/B test or comparison.
>
> **Output:** required n per group (or achievable power/MDE), the four inputs that produced it, and a runnable snippet.

## The four interlocking quantities

Fix any three; the fourth is determined:

| Quantity | Meaning | Conventional default |
|---|---|---|
| **α** (significance) | tolerated false-positive rate | **0.05** |
| **power** (1 − β) | probability of detecting a true effect of the target size | **0.80** (Cohen 1988) |
| **effect size / MDE** | the smallest effect worth detecting | business-meaningful; else Cohen d = 0.2/0.5/0.8 |
| **n** | sample size (per group) | the output you usually solve for |

## Procedure

1. **Pin the MDE first** — the smallest effect that would change the decision. Prefer a business-meaningful number (e.g., "a 1.5-point conversion lift pays for the change"); fall back to Cohen's conventions only when no pilot/benchmark exists.
2. **Pick α and power** (defaults 0.05 / 0.80 unless the cost of a false positive/negative argues otherwise).
3. **Match the calculation to the planned test** (two-proportion for conversion rates, two-sample t for a continuous mean, etc.).
4. **Solve for n** and report it **per group**, plus the total and the expected experiment duration given traffic.
5. **If the sample is fixed** (you can't get more), invert it: report the **power** and the **MDE** that n can actually detect — and warn loudly if power < 0.80 (the result will be hard to interpret either way → underpowered-study pitfall #8).

## Snippets (Tier-1 tooling)

```python
# continuous outcome: n per group for a medium effect (d=0.5), two-sided, 80% power
from statsmodels.stats.power import TTestIndPower
n = TTestIndPower().solve_power(effect_size=0.5, alpha=0.05, power=0.80, alternative="two-sided")
print(f"n per group ≈ {n:.0f}")
```

```python
# conversion rates: n per group to detect baseline 5% → 6.5% (a 1.5pp MDE)
from statsmodels.stats.proportion import proportion_effectsize
from statsmodels.stats.power import NormalIndPower
es = proportion_effectsize(0.065, 0.05)
n = NormalIndPower().solve_power(effect_size=es, alpha=0.05, power=0.80, alternative="two-sided")
print(f"n per group ≈ {n:.0f}")
```

## Guardrails
- **Compute n before launch, not after.** Post-hoc "observed power" on a finished study is misleading — don't do it.
- A null result from an **underpowered** study is *not* evidence of no effect — report the CI and the MDE the study could detect ("we could only have detected effects ≥ X").
- The randomization unit must match the unit of independence (user, not session) — see [`../../knowledge/experiment-design-and-ab-testing.md`](../../knowledge/experiment-design-and-ab-testing.md).
