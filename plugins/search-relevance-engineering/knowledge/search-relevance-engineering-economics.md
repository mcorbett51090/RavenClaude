# Search & Relevance Engineering Unit Economics

> The arithmetic behind the team's house opinions. Every formula here is reproduced in [`../scripts/search_relevance_engineering_calc.py`](../scripts/search_relevance_engineering_calc.py) so the math is auditable. All multipliers/benchmarks are `[unverified — training knowledge]` — supply the client's actual figures (§3 #8).

## 1. NDCG is the graded-relevance metric (§3 #1)

```
DCG@k  = sum( rel_i / log2(i + 1) for i in 1..k )   # i is the rank, starting at 1
IDCG@k = DCG of the ideal ordering (relevances sorted descending)
NDCG@k = DCG@k / IDCG@k                              # in [0, 1]
```

The `log2(i+1)` discount means a relevant document at rank 1 contributes `rel/1`, at rank 3 only `rel/2` — ranking the best results highest is what NDCG rewards.

## 2. MRR and precision@k for the simpler cases (§3 #1)

```
MRR          = mean( 1 / rank_of_first_relevant )   # known-item search
precision_at_k = relevant_in_topk / k
```

MRR cares only about the first relevant result (good for navigational queries); precision@k cares about the whole top-k page.

## 3. Recall gates precision (§3 #5)

```
if relevant_doc not in candidate_set: no ranking model can surface it
```

A precision/ranking fix on a low-recall candidate set is wasted effort — secure matching and query expansion first, then optimize ordering.

## 4. Latency budget bounds relevance work (§3 #4)

```
total_latency = query_parse + match + fetch + rescore
fits_budget   = p95(total_latency) <= latency_budget
```

Each relevance lever (bigger candidate set, rescoring, query expansion) adds latency; tune relevance within the p95 budget rather than chasing NDCG into a timeout.
