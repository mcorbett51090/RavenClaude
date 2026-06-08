# Relevance Judgment Set — `<system / corpus name>`

> Graded relevance annotations for offline evaluation. Scale: 0=not relevant,
> 1=marginally relevant, 2=relevant, 3=highly relevant.

- **System under test:** `<index name, query mode, model version>`
- **Date:** `<date>` · **Annotator(s):** `<names or IDs>`
- **Cohen's kappa (overlap set):** `<value>` · **Overlap query count:** `<N>`
- **Query distribution:** head `<N>` · torso `<N>` · tail `<N>`
- **Total query–document pairs:** `<N>`

---

## Annotation guidelines (inline summary)

> Full guidelines: `<link or file>`

| Grade | Meaning | Example |
|---|---|---|
| 3 | Highly relevant — the ideal result for this query | `<example>` |
| 2 | Relevant — clearly on-topic, useful | `<example>` |
| 1 | Marginally relevant — tangentially related | `<example>` |
| 0 | Not relevant | `<example>` |

---

## Judgment entries

| query_id | query_text | doc_id | doc_title | relevance | annotator | date |
|---|---|---|---|---|---|---|
| q001 | `<query text>` | d001 | `<document title>` | 3 | `<annotator>` | `<date>` |
| q001 | `<query text>` | d002 | `<document title>` | 1 | `<annotator>` | `<date>` |
| q002 | `<query text>` | d003 | `<document title>` | 2 | `<annotator>` | `<date>` |
| q002 | `<query text>` | d004 | `<document title>` | 0 | `<annotator>` | `<date>` |

_Add one row per (query, document) pair. Every query should have ≥ 5 judged documents from the_
_pooled candidate set. Queries with only 1–2 judged documents produce unreliable nDCG@k scores._

---

## Baseline metrics

Computed with `scripts/search_eval.py` against this judgment set.

| Metric | k | Value | Date computed |
|---|---|---|---|
| nDCG | 10 | `<value>` | `<date>` |
| MRR | — | `<value>` | `<date>` |
| recall | 20 | `<value>` | `<date>` |
| precision | 10 | `<value>` | `<date>` |

---

## Worst-10 queries by nDCG@10

| query_id | query_text | nDCG@10 | Suspected failure mode |
|---|---|---|---|
| `<id>` | `<text>` | `<score>` | `<tokenization / synonym gap / field weight / semantic gap>` |

---

## Changelog

| Date | Change | Author |
|---|---|---|
| `<date>` | Initial judgment set (N queries, N pairs) | `<author>` |

---

_Handoff: share this file with `relevance-engineer` (BM25/analyzer tuning) and/or_
_`vector-retrieval-engineer` (semantic gap queries) as indicated by the failure modes above._
