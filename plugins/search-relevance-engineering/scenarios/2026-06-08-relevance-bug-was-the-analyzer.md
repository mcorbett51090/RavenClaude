---
scenario_id: 2026-06-08-relevance-bug-was-the-analyzer
contributed_at: 2026-06-08
plugin: search-relevance-engineering
product: indexing
product_version: "n/a"
scope: likely-general
tags: [analyzer, mapping, recall, tokenization]
confidence: medium
reviewed: false
---

## Problem

Users reported that exact product codes returned nothing, and the team started adding ranking boosts. The risk: a relevance bug is usually a mapping/analyzer bug, and tuning the ranking formula on a candidate set that never contains the right document is wasted effort — you can't rank what you didn't retrieve (§3 #2 #5).

## Context

- Corpus: catalog with alphanumeric product codes.
- Constraint: analyzer/tokenization decisions ARE relevance decisions; recall comes before precision (§3 #2 #5).
- The team reached for boosts before checking analysis.

## Attempts

- Tried: **traced how the code was analyzed at index and query time.** Outcome: a standard analyzer split the alphanumeric code so the exact term never matched — a recall failure at analysis time (§3 #2).
- Tried: **fixed the mapping/analyzer** (keyword field + targeted analysis) to preserve the code as a matchable token (§3 #2 #5). Outcome: the right documents entered the candidate set.
- Tried: **re-measured NDCG on the judgment list** rather than trusting the spot-check (§3 #1). Outcome: relevance recovered without any ranking-formula change.

## Resolution

The fix was an **analyzer/mapping correction to secure recall**, validated on the judgment list — **not** a stack of ranking boosts. The output was the analyzer root-cause, the recall fix, and the re-measured NDCG.

**Action for the next consultant hitting this pattern:** **check the analyzer/mapping before the ranking formula, and secure recall before precision.** A no-match bug is almost always tokenization/analysis. Re-measure NDCG to confirm, don't trust the spot-check. See Tree 2 and the `fix-analyzer` skill.

Benchmark figures are segment-/region-/date-dependent — treat as `[unverified — training knowledge]` and validate against the client's own data before any deliverable (§3 #8).
