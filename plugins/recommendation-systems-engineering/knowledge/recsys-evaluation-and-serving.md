# Knowledge: Recsys Evaluation & Serving

> **Last reviewed:** 2026-07-21 · **Confidence:** high for the evaluation and serving patterns (provider-agnostic, stable); specific ANN-index/library specifics are volatile — re-verify at use.
> Source of truth for [`evaluate-recommenders`](../skills/evaluate-recommenders/SKILL.md) and [`handle-cold-start-and-serving`](../skills/handle-cold-start-and-serving/SKILL.md). Re-read on demand.

Two truths govern this file: **offline metrics filter, the online A/B decides**; and **train/serve parity + a fallback are the difference between a demo and production.**

## Offline metrics (per stage)

| Metric | Stage | Measures | Watch out |
|---|---|---|---|
| **Recall@k** | Retrieval | Did the candidate set contain the relevant items? | Report with candidate count — recall is trivial at large k |
| **Precision@k** | Ranking | Fraction of top-k that are relevant | Insensitive to order within k |
| **nDCG@k** | Ranking | Ranked quality with position discounting | The workhorse ranking metric |
| **MAP** | Ranking | Mean average precision across users | Good for binary relevance |
| **Coverage** | Guardrail | % of catalog ever recommended | Low = filter bubble |
| **Diversity (intra-list)** | Guardrail | Dissimilarity within a recommendation list | Too low = repetitive shelf |
| **Novelty / serendipity** | Guardrail | Non-obvious, non-popular hits | Balances accuracy vs discovery |

## The evaluation traps (why offline ≠ online)

1. **Random splits leak the future.** Recommenders predict forward; split **temporally** or the metrics are fiction.
2. **Feedback loop / position bias.** Logged data over-represents what the old model showed at good positions. Offline metrics reward mimicking the old model. Use bias-aware or counterfactual/off-policy estimation, and treat offline as directional.
3. **No baseline.** Without popularity as the bar, "better" is unfalsifiable.
4. **Train/serve skew.** Features computed differently at train vs serve time silently wreck online performance — a top cause of "won offline, flat online."
5. **Popularity leakage.** A feature that encodes global popularity can inflate offline metrics without adding personalization value.
6. **Metric mismatch.** Optimizing nDCG when the business cares about downstream conversion — the A/B is the arbiter of the real objective.

## The online A/B is the verdict

- **Primary metric** tied to the business objective (engagement, conversion, retention).
- **Guardrails:** latency, catalog coverage/diversity, revenue, complaint/unsub rate.
- **Design** (power/MDE, assignment, duration) with `experimentation-growth-engineering` / `applied-statistics`.
- Ship on the **online** result. Offline is the filter that decides what earns an A/B slot.

## Serving

```
request -> [retrieval: ANN over embeddings | precomputed candidates]
        -> [feature fetch: online store, parity with training]
        -> [ranking model]
        -> [re-rank: diversity + business rules]
        -> response   (fallback: popularity on timeout/error)
```

- **Budget latency across stages** and hold the pipeline to the SLA.
- **ANN index** (FAISS / ScaNN / HNSW-class) for embedding retrieval — never brute-force the catalog at request time.
- **Precompute/cache** for stable users where freshness allows; reserve real-time compute for where it pays.
- **Online feature store** with train/serve parity — share the feature definition, don't reimplement it.
- **Fallback to popularity on timeout or error.** A blank or erroring shelf is worse than a generic-but-instant one.

## The feedback loop (a system risk, not a metric)

A recommender trains on data its own recommendations produced. Left unmanaged, popularity concentrates, exploration dies, and the catalog's long tail goes dark. Mitigate with an **exploration budget** (epsilon/bandit), **diversity guardrails**, and **honest logging** of served positions + outcomes so the next model can debias. This is why coverage/diversity are first-class metrics, not vanity.

## The failure modes this prevents

| Skipped safeguard | Failure |
|---|---|
| Temporal split | Offline metrics inflated by leaked future interactions |
| Popularity baseline | Can't tell if the model is worth its complexity |
| Train/serve parity | Model wins offline, flat or worse online |
| Diversity/coverage guardrail | Accurate filter bubble that caps catalog value |
| Serving fallback | Slow/failed model → blank or erroring shelf |
| Exploration budget | Feedback loop starves the long tail forever |
