# AI / RAG Engineering scenarios bank

Dated, scope-tagged, **unverified** engagement narratives for the `ai-rag-engineering` plugin (the marketplace scenarios pattern; see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md)).

**How to use these:** a scenario is a *secondary* source. Surface a matching one only behind the mandatory unverified-scenario preamble, and never let it override the cited [`../knowledge/`](../knowledge/) bank or a qualified authority (§2). No user data / prompt PII (§2). Benchmark figures are `[unverified — training knowledge]` (§3 #8).

## Index

| Scenario | Scope | Pattern |
|---|---|---|
| [`2026-06-08-swapped-model-it-was-retrieval.md`](./2026-06-08-swapped-model-it-was-retrieval.md) | likely-general | A team swapped to a bigger model to fix wrong answers; the bug was recall@k |
| [`2026-06-08-more-context-made-it-worse.md`](./2026-06-08-more-context-made-it-worse.md) | likely-general | Stuffing more chunks into the prompt raised cost and lowered answer quality |
| [`2026-06-08-shipped-without-eval.md`](./2026-06-08-shipped-without-eval.md) | likely-general | A 'small' chunking tweak silently regressed faithfulness because there was no eval |

## See also
- [`../knowledge/ai-rag-engineering-decision-trees.md`](../knowledge/ai-rag-engineering-decision-trees.md) — the trees these scenarios traverse.
