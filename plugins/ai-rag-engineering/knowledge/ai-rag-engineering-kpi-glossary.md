# AI / RAG Engineering KPI Glossary

> The team's canonical metric definitions. Every metric carries a **definition**, a **window**, and a **baseline** before it ships (CLAUDE.md §3 #1). Benchmark ranges are `[unverified — training knowledge]` unless a dated source is attached — confirm against a current source before using in a deliverable (§3 #8).

## Retrieval & eval

| Metric | Definition | Window | Note |
|---|---|---|---|
| **Recall@k** | Relevant passages in top-k ÷ total relevant | Per query set | Caps generation quality — measure first (§3 #1). |
| **Precision@k** | Relevant passages in top-k ÷ k | Per query set | Low precision feeds distractors into the prompt (§3 #5). |
| **Faithfulness** | Is the answer grounded in retrieved context? | Per query set | Citations are how you measure it (§3 #7). |
| **Answer-relevance** | Does the answer address the query? | Per query set | High faithfulness + low relevance = right source, wrong answer. |

## Ingestion & chunking

| Knob | Definition | Note |
|---|---|---|
| **Chunk size** | Tokens per chunk | Interacts with context budget and recall (§3 #2 #5). |
| **Overlap** | Shared tokens between adjacent chunks | Reduces answer-splitting at boundaries (§3 #2). |
| **Structure-awareness** | Respect tables/sections/headings | Keeps answering units intact (§3 #2). |
| **Metadata** | Fields for pre-filtering retrieval | Narrows the search space before ranking. |

## Serving & cost

| Metric | Definition | Window | Note |
|---|---|---|---|
| **Cost per request** | (input + output tokens) × per-1k price | Per request | Context tokens dominate input (§3 #5). |
| **Context utilization** | Prompt tokens ÷ context window | Per request | Headroom for output; over-stuffing degrades quality (§3 #5). |
| **p95 latency** | 95th-percentile end-to-end response time | Rolling | More context raises latency (§3 #5). |
| **Hybrid fusion** | Combine BM25 + vector ranks (e.g. RRF) | Per query | Default for most corpora (§3 #6). |

## The rule

A metric without a **window** and a **baseline** is not a finding — it's a number (§3 #1). A benchmark without a **source URL + retrieval date** is `[unverified — training knowledge]` (§3 #8).
