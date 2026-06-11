---
description: "Build a DevRel scorecard — instrument the activation funnel, compute TTFV/activation/conversion, separate vanity inputs from outcomes, and name the decision each metric informs."
---

# /build-devrel-metrics

Spawn `devrel-lead` (with `docs-and-dx-engineer` for funnel instrumentation) to build a DevRel
scorecard the exec team will trust.

## What it does

1. Instruments the activation funnel with concrete events.
2. Computes core metrics via [`../scripts/devrel_calc.py`](../scripts/devrel_calc.py): time-to-first-value, activation rate, funnel conversion, content ROI, community health.
3. Splits the scorecard into **outcome metrics** (lead with these) and **vanity inputs** (paired or cut).
4. Assigns each metric a cadence and the decision it triggers.

## Usage

```
/build-devrel-metrics
```

Then share the metrics you currently track and your data sources. The agent applies
[`developer-experience-measurement`](../skills/developer-experience-measurement/SKILL.md).

## Good inputs

- Current metrics + where each comes from.
- Funnel event availability (what you can actually instrument today).
