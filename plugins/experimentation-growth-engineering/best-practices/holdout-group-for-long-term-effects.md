# Maintain a holdout group to measure cumulative long-term effects

**Status:** Pattern
**Domain:** Experimentation / long-term measurement
**Applies to:** `experimentation-growth-engineering`

---

## Why this exists

Individual A/B tests measure short-window effects. A product that ships 40
experiments per quarter measures each one in isolation but may not detect the
cumulative effect on retention, revenue, or user fatigue 6 months later. A
global holdout group — a small slice of users (typically 1–5%) held out of all
experiments for a defined period — provides the comparison point between "full
experiment programme" and "no experiments" on long-term metrics. Without it,
a team can win every individual A/B test and still erode long-term engagement
because of compounding interactions.

## How to apply

1. Designate a holdout bucket (e.g. 2% of traffic) at the traffic-allocation
   layer, before any experiment assignment.
2. This bucket receives no experimental treatments and no test features during
   the holdout window.
3. At the end of the holdout window (typically quarterly), compare long-term
   metrics between the holdout group and the shipped-everything population.

```python
HOLDOUT_PCT = 2  # 2% of users held out of all experiments

def is_holdout(user_id: str) -> bool:
    bucket = int(hashlib.md5(f"global-holdout:{user_id}".encode()).hexdigest(), 16) % 100
    return bucket < HOLDOUT_PCT

def assign_experiment(user_id: str, experiment: Experiment) -> str | None:
    if is_holdout(user_id):
        return None  # Holdout — no treatment assigned
    return experiment.assign(user_id)
```

Route the long-term metric comparison to `applied-statistics` — the holdout
group analysis requires accounting for novelty effects, seasonality, and
cohort composition.

**Do:**
- Keep the holdout bucket stable (same users throughout the window); rotating
  it defeats the purpose.
- Disclose the holdout to the product team so they don't misattribute holdout
  users' different behaviour to a bug.
- Refresh the holdout cohort at the start of each measurement window so
  long-running users don't permanently miss features.

**Don't:**
- Make the holdout larger than 5% — the opportunity cost of withholding all
  features from too many users is real.
- Use the holdout group for individual experiment significance testing — it is
  a programme-level measurement, not an experiment control.
- Forget to exclude holdout users from individual experiment analyses (they
  should be neither treatment nor control in any A/B test).

## Edge cases / when the rule does NOT apply

- Early-stage products (< 6 months) with a small user base where a holdout
  bucket is a material fraction: skip holdout until you have the traffic budget.
- Compliance-driven feature changes (legal requirements): the holdout cannot
  withhold legally-mandated changes.

## See also

- [`../agents/experimentation-architect.md`](../agents/experimentation-architect.md) — owns experiment programme design
- [`./mutual-exclusion-for-concurrent-experiments.md`](./mutual-exclusion-for-concurrent-experiments.md) — holdout is the outermost exclusion layer

## Provenance

Standard experimentation infrastructure pattern used at major A/B testing
platforms. The holdout group discipline is documented in Kohavi, Tang, and
Xu "Trustworthy Online Controlled Experiments" (Cambridge University Press).
Statistical analysis of the holdout result routes to `applied-statistics`.

---

_Last reviewed: 2026-06-05 by `claude`_
