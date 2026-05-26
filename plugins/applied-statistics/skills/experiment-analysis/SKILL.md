---
name: experiment-analysis
description: Analyze a completed A/B test or experiment defensibly — check it against the pre-registered plan, run the primary-metric test, report effect size + CI (not just p), check guardrail metrics, apply a multiple-comparison correction across metrics/segments, and screen for the peeking/p-hacking pitfalls before declaring a winner. Used by `applied-statistician` (primary).
---

# Skill: experiment-analysis

> **Invoked by:** `applied-statistician` (primary). Pairs with [`../power-and-sample-size/SKILL.md`](../power-and-sample-size/SKILL.md) (run first, at design time) and [`../choose-statistical-test/SKILL.md`](../choose-statistical-test/SKILL.md) (names the underlying test).
>
> **When to invoke:** "is this A/B winner real?"; "the experiment finished — what does it say?"; "can we ship variant B?"
>
> **Output:** a verdict (ship / don't ship / inconclusive) backed by the primary-metric effect size + CI, the guardrail check, the multiplicity correction, and an explicit pitfall screen.

## Procedure

1. **Recover the analysis plan.** Was there a pre-registered primary metric, test, and stopping rule ([`../../templates/analysis-plan.md`](../../templates/analysis-plan.md))? If analysis decisions were made *after* seeing data, flag the p-hacking exposure (pitfall #1) and treat findings as exploratory.
2. **Check the stopping rule.** Was the test stopped at the planned sample, or stopped early when it "looked significant"? Early stopping on a fixed-horizon test = peeking (pitfall #3) → the nominal p-value is not valid; downgrade confidence.
3. **Run the primary-metric test** (via `choose-statistical-test`). Report the **effect size + confidence interval** as the headline — the p-value is secondary (pitfall #6). "Significant but the CI includes trivially small effects" is not a ship signal.
4. **Check guardrail metrics.** A primary-metric win that degrades a guardrail (latency, churn, revenue/user) is not a win. State each guardrail's movement + CI.
5. **Correct for multiplicity.** If you tested several metrics or segments, apply Holm/Bonferroni (confirmatory) or Benjamini-Hochberg (exploratory) — see [`../../knowledge/statistical-pitfalls.md`](../../knowledge/statistical-pitfalls.md). A "winning segment" found after slicing 10 ways is usually noise.
6. **Sanity-check for Simpson's paradox** (pitfall #4): does the aggregate result hold within key subgroups, or does the group mix drive it?
7. **Verdict** in plain language: ship / don't ship / inconclusive (underpowered) — with the effect, CI, and the main caveat.

## Output shape

```
Primary metric: <metric> — variant B <+X% / +X units>, 95% CI [<lo>, <hi>], p = <p>
Decision-relevant? <effect vs the MDE that justified the test>
Guardrails: <metric: movement + CI; pass/fail> ...
Multiplicity: <# metrics/segments tested; correction applied>
Pitfall screen: pre-registered? stopped at planned n? peeking? Simpson's?
Verdict: SHIP / DON'T SHIP / INCONCLUSIVE — <one-line reason + main caveat>
```

## Guardrails
- The headline is the **effect size + CI**, never a bare "p < 0.05."
- Early-stopped fixed-horizon tests and post-hoc segment-mining both produce false winners — name them when present.
- An inconclusive (underpowered) result is an honest verdict; don't manufacture a winner.
