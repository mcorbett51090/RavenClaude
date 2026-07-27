# Recsys Evaluation Report — <model / experiment>

> Records one recommender evaluation, offline then online. A model does not ship on an offline win alone — the online A/B is the verdict. Owned by [`recsys-implementation-engineer`](../agents/recsys-implementation-engineer.md); eval strategy from [`recsys-architect`](../agents/recsys-architect.md).

## 0. Context

- **Model / version:** <...>
- **Compared against:** <baseline + prior production model>
- **Split:** temporal — train ≤ <date>, test > <date>  ← *must be temporal, not random*

## 1. Offline results (vs baseline)

| Metric | Stage | Baseline | Prod model | New model | Δ vs prod |
|---|---|---|---|---|---|
| Recall@k (k=<>) | Retrieval | | | | |
| nDCG@k (k=<>) | Ranking | | | | |
| MAP | Ranking | | | | |
| Precision@k | Ranking | | | | |
| Coverage | Guardrail | | | | |
| Diversity (intra-list) | Guardrail | | | | |
| Novelty | Guardrail | | | | |

- **Beats baseline?** <yes/no> — if no, stop here.
- **Bias caveats:** <feedback-loop/position-bias handling; is offline directional only?>

## 2. Correctness checks (BLOCKING before A/B)

- [ ] Temporal split (no future leakage)
- [ ] Popularity baseline wired into the same harness
- [ ] Train/serve feature parity verified
- [ ] No popularity leakage in features
- [ ] Metric matches the stage
- [ ] Serving path meets latency SLA with popularity fallback

## 3. Online A/B (the verdict)

- **Design:** primary metric <>, guardrails <latency / diversity / revenue / complaints>, MDE <>, duration <>, assignment <>
- **Results:**

| Metric | Control | Treatment | Δ | Significant? |
|---|---|---|---|---|
| Primary <> | | | | |
| Guardrail: latency | | | | |
| Guardrail: diversity/coverage | | | | |
| Guardrail: revenue | | | | |
| Guardrail: complaints/unsub | | | | |

- **Verdict:** ship / iterate / kill — **why**
- **If offline ⟂ online:** diagnosis (feedback bias / metric mismatch / train-serve skew / popularity leakage / guardrail regression)

## 4. Sign-off

| Gate | Owner | Status |
|---|---|---|
| Offline beats baseline (temporal) | recsys-implementation-engineer | ☐ |
| Correctness checks green | recsys-implementation-engineer | ☐ |
| Online A/B is the decision | experimentation-growth-engineering | ☐ |
