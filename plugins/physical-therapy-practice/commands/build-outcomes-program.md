---
description: "Build a functional-outcomes program — choose standardized measures by region, set the intake/interval/discharge cadence and MCID thresholds, tie outcomes to medical necessity, and assess MIPS/value-based readiness."
---

# /build-outcomes-program

Spawn `outcomes-and-quality-analyst` to design a functional-outcomes and quality-reporting program.

## What it does

1. Selects standardized, region-appropriate outcome measures.
2. Sets the collection cadence (intake / interval / discharge) and MCID thresholds.
3. Computes change vs. MCID via [`../scripts/pt_calc.py`](../scripts/pt_calc.py) `outcome_change_vs_mcid`.
4. Ties functional progress to the medical-necessity rationale and assesses quality-reporting readiness.

## Usage

```
/build-outcomes-program
```

Then share your conditions/regions treated and current measurement (if any). The agent applies
[`functional-outcomes-and-quality-reporting`](../skills/functional-outcomes-and-quality-reporting/SKILL.md)
and the [`outcomes-tracking-scorecard`](../templates/outcomes-tracking-scorecard.md) template.

> Decision-support only — verify MIPS/value-based specifics against current program rules and a
> compliance professional.
