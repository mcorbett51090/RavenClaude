---
description: "Audit the developer onboarding funnel — instrument sign-up → first-success, find the steepest drop, diagnose the cause, and return the highest-leverage fix with the metric to track it."
---

# /audit-developer-onboarding

Spawn `docs-and-dx-engineer` to diagnose where the onboarding funnel loses developers and how to fix it.

## What it does

1. Maps the funnel: `sign_up → credential → first_call → first_success`.
2. Identifies the steepest drop and forms a cause hypothesis (friction, prerequisite, error quality, conceptual gap).
3. Rewrites the getting-started path to remove the friction — declared prerequisites/versions, real runnable commands, a verification step.
4. Names the metric (time-to-first-value, activation rate) to confirm the fix.

## Usage

```
/audit-developer-onboarding
```

Then paste your current quickstart/getting-started and any funnel data you have. The agent applies
[`developer-experience-measurement`](../skills/developer-experience-measurement/SKILL.md) and uses
[`../scripts/devrel_calc.py`](../scripts/devrel_calc.py) for the funnel math.

## Good inputs

- The actual quickstart text/commands (so hidden steps can be found).
- Stage-by-stage counts if instrumented; otherwise the agent will specify what to instrument first.
