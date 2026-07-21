---
name: evaluate-recommenders
description: "Evaluate recommenders correctly — a temporal train/test split, per-stage offline metrics (recall@k, precision@k, nDCG, MAP, coverage, diversity, novelty) against a popularity baseline, AND the online A/B that is the real verdict. Use to build an eval harness or diagnose an offline-vs-online gap."
---

# Skill: Evaluate Recommenders

Offline metrics **filter**; the online A/B **decides**. Recommender evaluation is uniquely treacherous because offline metrics are computed on data the *old* model's exposures generated — they are biased toward what was already shown. This skill builds an honest offline harness and connects it to the online verdict.

## When to use

- Standing up an offline evaluation harness.
- Comparing recommender models/versions.
- Diagnosing why an offline win didn't reproduce online.

## Steps

1. **Split temporally.** Train on the past, test on the future. A random split leaks future interactions and inflates every metric — the single most common recsys evaluation bug.
2. **Wire in the popularity baseline.** Every metric is reported for the candidate model *and* the baseline. A model that doesn't beat popularity offline will not beat it online.
3. **Use the metric that matches the stage.** Recall@k (+ candidate count) for retrieval; nDCG / MAP / precision@k for ranking. See [`../../knowledge/recsys-evaluation-and-serving.md`](../../knowledge/recsys-evaluation-and-serving.md).
4. **Report guardrails, not just accuracy.** Catalog coverage, diversity (intra-list), and novelty catch the "accurate filter bubble" — a model that only recommends head items.
5. **Account for the feedback loop / position bias.** Offline data over-represents what was shown at good positions. Use bias-aware metrics or counterfactual/off-policy estimation where you can, and treat offline as directional.
6. **Design the online A/B as the verdict.** Primary metric (e.g. engagement/conversion) + guardrails (latency, diversity, revenue, complaint rate), with power/MDE from `experimentation-growth-engineering` / `applied-statistics`. Ship on the online result, not the offline one.
7. **When offline and online disagree, diagnose it.** Usual culprits: feedback-loop bias, metric mismatch, train/serve skew, popularity leakage in features, or a guardrail regression masking a headline gain.

## Anti-patterns

- Random train/test split (leaks the future).
- No baseline, so "better" is unmeasurable.
- One global metric hiding which stage is weak.
- Optimizing accuracy alone → a filter-bubble recommender with low coverage.
- Trusting offline as the verdict and skipping the A/B.
- Ignoring train/serve skew when offline and online disagree.

## Output

An eval harness + report: temporal split → per-stage metrics vs baseline → coverage/diversity/novelty guardrails → bias caveats → the online A/B plan and its verdict. Capture it in the [`recsys-eval-report`](../../templates/recsys-eval-report.md).
