# Search & Relevance Engineering scenarios bank

Dated, scope-tagged, **unverified** engagement narratives for the `search-relevance-engineering` plugin (the marketplace scenarios pattern; see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md)).

**How to use these:** a scenario is a *secondary* source. Surface a matching one only behind the mandatory unverified-scenario preamble, and never let it override the cited [`../knowledge/`](../knowledge/) bank or a qualified authority (§2). No query/user PII (§2). Benchmark figures are `[unverified — training knowledge]` (§3 #8).

## Index

| Scenario | Scope | Pattern |
|---|---|---|
| [`2026-06-08-relevance-bug-was-the-analyzer.md`](./2026-06-08-relevance-bug-was-the-analyzer.md) | likely-general | A 'ranking' problem was a tokenization bug — no boost would have fixed it |
| [`2026-06-08-offline-win-didnt-transfer.md`](./2026-06-08-offline-win-didnt-transfer.md) | likely-general | An offline NDCG win failed to move CTR until the judgment list was fixed |
| [`2026-06-08-ndcg-chased-into-timeout.md`](./2026-06-08-ndcg-chased-into-timeout.md) | likely-general | Chasing NDCG with heavier rescoring blew the latency budget |

## See also
- [`../knowledge/search-relevance-engineering-decision-trees.md`](../knowledge/search-relevance-engineering-decision-trees.md) — the trees these scenarios traverse.
