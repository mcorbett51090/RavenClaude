# search-relevance-engineering

A **Search & Relevance Engineering specialist team** for a search relevance engineer, ranking analyst, or platform lead accountable for search quality, latency, and conversion. It measures relevance with NDCG/MRR rather than vibes, treats analyzer/mapping decisions as relevance decisions, builds a judgment list before tuning, and validates online with A/B because offline gains don't always transfer.

> Inherits the [`ravenclaude-core`](../ravenclaude-core/) protocols (claim-grounding, structured output, decision review). Engine-flexible, corpus-explicit (greenfield search | relevance-tuning | reindex/mapping fix | latency reduction).

## What you get

| Surface | Contents |
|---|---|
| **4 agents** | `search-relevance-lead`, `relevance-tuning-analyst`, `indexing-mapping-specialist`, `query-performance-specialist` |
| **5 skills / commands** | `measure-relevance` · `build-judgment-list` · `fix-analyzer` · `validate-online` · `set-latency-budget` |
| **4-file knowledge bank** | KPI glossary · unit economics · 2025–2026 context · Mermaid decision trees |
| **4 templates** | scorecard · exec readout · relevance-eval-sheet.md · index-sizing-sheet.md |
| **1 advisory hook** | flags anti-patterns (unbaselined metric, unsourced benchmark, query/user PII) in generated deliverables |
| **`scripts/search_relevance_engineering_calc.py`** | stdlib calculator — `relevance` · `latency-budget` · `index-sizing` |

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install search-relevance-engineering@ravenclaude
```

## Quickstart

> "Our search results feel bad — how do we actually fix relevance?"

The `search-relevance-lead` scopes the problem, routes to `relevance-tuning-analyst` (or a sibling specialist), and synthesizes a ranked action plan with owners, dates, and expected metric movement.

## What it is not

a recommendation-systems research lab, a database-administration function, or a UX/product-copy authority. It does not own personalized recsys modeling, cluster ops, or UX design — those route to the qualified authority.
