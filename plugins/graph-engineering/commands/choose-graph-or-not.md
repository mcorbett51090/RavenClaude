---
description: "Decide whether a workload should be a graph (LPG or RDF) or stay relational / RAG / KV. Walk the decision tree before any labels."
argument-hint: "[the workload or question]"
---

# Choose graph or not

You are running `/graph-engineering:choose-graph-or-not` for `$ARGUMENTS`. Apply [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps

1. Name the read question and the write/rollback story.
2. Traverse [`../knowledge/graph-vs-relational-decision-tree.md`](../knowledge/graph-vs-relational-decision-tree.md).
3. Verdict: LPG / RDF / stay relational / stay RAG / stay KV.
4. If no — name the neighbor plugin and stop.
5. If LPG — point at `/model-property-graph`. If retrieval-graph — demand the BM25 baseline, then `/construct-retrieval-graph`.

## Guardrails

- Advisory only. No live database.
- GraphQL → `graphql-engineering`. Microsoft Graph API → `microsoft-graph`.
- See [`../skills/choose-graph-or-not/SKILL.md`](../skills/choose-graph-or-not/SKILL.md).
