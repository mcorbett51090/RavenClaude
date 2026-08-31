---
name: model-property-graph
description: "Design a labeled property graph — labels, typed directed relationships, business-key identity, temporal edges, and a supernode plan. Fill templates/graph-data-model.md before any CREATE."
---

# Skill: model-property-graph

> **Invoked by:** `graph-data-modeler` (primary).
>
> **When to invoke:** "model this as a graph"; "what labels and rel types?"; "this celebrity node kills traversals."
>
> **Output:** a filled [`../../templates/graph-data-model.md`](../../templates/graph-data-model.md) plus lint-clean MERGE sketches the user runs.

## Procedure

1. Confirm `choose-graph-or-not` already returned **LPG**. If not, go back.
2. Read [`../../knowledge/lpg-modeling-catalog.md`](../../knowledge/lpg-modeling-catalog.md).
3. Name **labels** (types, not states) and **business keys**.
4. **Type every relationship** and give it a direction. Put link payload on the edge.
5. Write a **supernode plan** for any celebrity label (partition, start from the other side, bound hops).
6. Emit `MERGE`-on-business-key sketches. No untyped `-[]-`. No unbounded `*`.
7. Run [`../../scripts/lint_graph_shape.py`](../../scripts/lint_graph_shape.py) on snippets before handing them over.

## Guardrails

- Untyped `()-[]-()` is a bug.
- `CREATE` on every ingest duplicates the graph — `MERGE` on the business key.
- RDF wants IRIs + SPARQL, not this skill.
