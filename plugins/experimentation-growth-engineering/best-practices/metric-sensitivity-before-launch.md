# Validate metric sensitivity before committing to an experiment design

**Status:** Primary diagnostic
**Domain:** Experimentation / metric selection
**Applies to:** `experimentation-growth-engineering`

---

## Why this exists

An experiment designed around a metric that doesn't move measurably even for
known large effects is a waste of the traffic budget. Teams run a 4-week test,
get a flat result, and conclude "no effect" — but the metric may simply have
too low a sensitivity (high variance, low base rate, slow seasonality) to detect
a realistic lift in that window. Metric sensitivity analysis (using historical
data to estimate the minimum detectable effect and the required sample size)
before committing to the experiment design routes this class of failure upstream
to `applied-statistics`, where it belongs, before any traffic is allocated.

## How to apply

Before finalising an experiment plan, validate the primary metric's sensitivity
with historical data:

1. Pull 2–4 weeks of historical values for the proposed primary metric.
2. Calculate the metric's mean and variance (or conversion rate and denominator).
3. Route to `applied-statistics` for power analysis: given N% traffic allocation
   and a realistic MDE (minimum detectable effect), how many days/users are needed
   to achieve 80% power?
4. If the answer is > 8 weeks or > total available traffic, the metric is not
   sensitive enough for the planned experiment window — consider a more sensitive
   proxy or a longer pre-commitment.

```python
# Sensitivity sanity check (not the power calculation — route that to applied-statistics)
import numpy as np

historical_values = load_metric_history("checkout_completion_rate", days=28)
mean = np.mean(historical_values)
std = np.std(historical_values)
# Coefficient of variation — high CV = noisy metric = low sensitivity
cv = std / mean
print(f"Mean: {mean:.3f}, CV: {cv:.2f}")
# Route to applied-statistics with these inputs for the full power calc
```

**Do:**
- Validate metric sensitivity before any traffic is allocated.
- Use at least 2 weeks of historical data for seasonal stability.
- Distinguish between a sensitive metric (low variance, high base rate) and a
  business-significant metric (high-value, low frequency) — experiments may need
  both, requiring a hierarchy of primary and secondary metrics.

**Don't:**
- Choose the primary metric based on what sounds important without checking its
  historical variance.
- Substitute "we'll run it longer if needed" for a pre-experiment power estimate
  — that is ad-hoc peeking dressed as planning.
- Conduct the power calculation yourself — route it to `applied-statistics`.

## Edge cases / when the rule does NOT apply

- Experiments where the primary metric is binary and high-frequency (e.g. a
  click-through rate with millions of daily impressions): sensitivity is almost
  always sufficient; a quick back-of-envelope confirms it.

## See also

- [`../agents/experimentation-architect.md`](../agents/experimentation-architect.md) — owns experiment design and routes to applied-statistics
- [`./guardrail-metrics-on-every-experiment.md`](./guardrail-metrics-on-every-experiment.md) — guardrail metrics need sensitivity validation too
- [`./no-peeking-pre-register.md`](./no-peeking-pre-register.md) — pre-registration requires knowing the MDE and duration up front

## Provenance

Standard A/B test statistical practice. Power analysis before experiment launch
is a foundational requirement in Kohavi et al. "Trustworthy Online Controlled
Experiments" and all major experimentation platform documentation. Statistical
analysis routes to `applied-statistics` per house opinion #1 from `CLAUDE.md` §2.

---

_Last reviewed: 2026-06-05 by `claude`_
