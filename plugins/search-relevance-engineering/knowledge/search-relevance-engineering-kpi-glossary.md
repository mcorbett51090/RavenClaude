# Search & Relevance Engineering KPI Glossary

> The team's canonical metric definitions. Every metric carries a **definition**, a **window**, and a **baseline** before it ships (CLAUDE.md §3 #1). Benchmark ranges are `[unverified — training knowledge]` unless a dated source is attached — confirm against a current source before using in a deliverable (§3 #8).

## Relevance metrics

| Metric | Definition | Window | Note |
|---|---|---|---|
| **NDCG@k** | DCG@k ÷ IDCG@k (graded relevance, log-discounted by rank) | Per query set | Rewards relevant docs ranked higher (§3 #1). |
| **MRR** | Mean of 1 ÷ rank-of-first-relevant | Per query set | Best for known-item / first-answer search (§3 #1). |
| **Precision@k** | Relevant in top-k ÷ k | Per query set | Top-of-page quality; pair with recall (§3 #5). |
| **Recall** | Relevant retrieved ÷ total relevant | Per query set | Secure first — can't rank what you didn't retrieve (§3 #5). |

## Index & analysis

| Knob | Definition | Note |
|---|---|---|
| **Analyzer** | Tokenizer + filters (stemming, synonyms, stopwords) | A relevance decision, not preprocessing (§3 #2). |
| **Mapping / field type** | How a field is indexed and matched | Wrong type silently breaks matching (§3 #2). |
| **Query expansion** | Synonyms / fuzziness to widen matching | A recall lever (§3 #5). |
| **Shard / replica** | Index partition / copy | Drives capacity and query latency (§3 #4 #7). |

## Online & latency

| Metric | Definition | Window | Note |
|---|---|---|---|
| **p95 latency** | 95th-percentile query latency | Rolling | The budget relevance work lives inside (§3 #4). |
| **CTR** | Clicks ÷ impressions on results | Rolling | The online relevance signal (§3 #6). |
| **A/B lift** | Variant metric − control metric | Per experiment | Offline win must transfer here (§3 #6). |
| **Position bias** | Higher ranks get clicked regardless of relevance | Per analysis | Confounds click-derived judgments (§3 #3 #6). |

## The rule

A metric without a **window** and a **baseline** is not a finding — it's a number (§3 #1). A benchmark without a **source URL + retrieval date** is `[unverified — training knowledge]` (§3 #8).
