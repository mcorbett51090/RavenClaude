---
description: "Read the referral-to-admission funnel — conversion rate by stage, time-to-admission, the leaking stage, and a root cause + owner for every declined referral — then connect activity to an average-daily-census target. A referral is not census until it converts."
argument-hint: "[funnel data, e.g. '80 referrals, 14 ineligible, 8 family-declined, 6 lost to competitor, 52 admits, 1.9-day avg time-to-admit']"
---

# Analyze the admissions funnel

You are running `/hospice-referral-sales:analyze-admissions-funnel`. Read the funnel for the data the user gave (`$ARGUMENTS`), using this plugin's `admissions-conversion-coach` discipline and the `admissions-funnel-analytics` skill.

## Steps

1. **Map the stages** — referral → eligibility screen → information visit → election → admission, with conversion and elapsed time at each. Flag real vs placeholder figures.
2. **Find the leak** — overall and stage conversion vs a benchmark _band_ (mark benchmarks `[example — calibrate to your program]`). Run `scripts/hospice_calc.py funnel` for the arithmetic.
3. **Root-cause every decline** — assign each to the taxonomy (ineligible / family-declined / lost to competitor / too-slow / patient died first / facility re-routed) **and an owner**. Traverse `## Decision Tree: Declined-referral root-cause`.
4. **Read time-to-admission & census** — the same-day rate, and (via `scripts/hospice_calc.py census`) the ADC and length-of-stay picture; flag a short LOS as a late-referral signal.
5. **Connect activity to census** — work back from the census target to the referral rate required.
6. Emit in the Output Contract format + the Structured Output JSON block.

## Guardrails

- A referral count is never census — report conversion, not raw volume.
- Every decline gets a root cause and an owner; "we lost some" is not a diagnosis.
- A short LOS is usually an upstream education problem, not an intake one.
- No patient-identifying data — counts and rates only.
