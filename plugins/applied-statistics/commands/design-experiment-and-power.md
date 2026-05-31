---
description: "Design an experiment or A/B test and size it: pre-register the plan, fix three of {alpha, power, MDE, n} and solve for n, and set a stopping rule before any data is collected."
argument-hint: "[the experiment, e.g. 'A/B test a new onboarding flow for conversion']"
---

# Design an experiment and run the power analysis

You are running `/applied-statistics:design-experiment-and-power`. Turn the user's intent (`$ARGUMENTS`) into a pre-registered, correctly-sized experiment design before a single row is collected, the way the `applied-statistician` agent would.

## When to use this

You are about to launch an A/B test or experiment and need the sample size, stopping rule, and analysis plan written down up front. NOT for analyzing a test that already ran (that is `/applied-statistics:analyze-experiment`), and NOT for an observational/fixed-budget dataset you cannot resize.

## Steps

1. **Name one primary metric and a directional hypothesis** before anything else (`design-pre-register-to-avoid-p-hacking.md`): metric, direction, segments, and guardrails written down — everything not in the plan is labeled *exploratory*.
2. **Anchor the MDE to a business-meaningful effect**, not Cohen's conventions — the smallest effect worth acting on for the decision (`design-power-and-sample-size-before-collecting.md`). Use the small/medium/large d = 0.2/0.5/0.8 anchors only as a labeled fallback when no pilot SD exists.
3. **Fix three of {alpha, power, MDE, n} and solve for n** (`design-power-and-sample-size-before-collecting.md`): conventions are alpha = 0.05, power = 0.80 — state them as conventions, and adjust when the cost of a false positive vs. false negative argues for it. Use the right power formula for the outcome type (t-test for continuous; proportion/count/survival have their own).
4. **Set the stopping rule** (`design-pre-register-to-avoid-p-hacking.md`): a fixed horizon ("do not look until n is reached") OR a named sequential/always-valid method — never "stop when it looks significant."
5. **Pick the analysis test up front** by traversing the decision tree on the outcome's data type and group structure (`test-match-the-test-to-the-data-type.md`), and name the multiplicity correction (FWER for confirmatory, FDR for exploratory) for any secondary metrics (`test-correct-for-multiple-comparisons.md`).
6. Produce the design doc + the runnable power snippet (Tier-1: `pingouin`/`statsmodels`), shaped per the plugin's `templates/experiment-design-doc.md` and `templates/power-analysis-worksheet.md`.

## Guardrails

- Never run a *post-hoc "observed-power"* calculation to justify a null — it is circular; report the MDE the design can detect instead.
- alpha = 0.05 / power = 0.80 are conventions, not laws — state them and adjust to the decision's cost asymmetry.
- A fixed-budget study cannot choose n; size the *detectable* MDE up front and decide whether that MDE is decision-useful before running.
