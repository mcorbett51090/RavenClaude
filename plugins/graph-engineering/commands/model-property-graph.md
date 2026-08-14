---
description: "Model a labeled property graph — labels, typed directed relationships, identity, supernodes — and emit MERGE sketches."
argument-hint: "[entities and relationships to model]"
---

# Model property graph

You are running `/graph-engineering:model-property-graph` for `$ARGUMENTS`. Apply [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps

1. Confirm the store decision is LPG (`/choose-graph-or-not` if not).
2. Fill [`../templates/graph-data-model.md`](../templates/graph-data-model.md).
3. Type every relationship; plan supernodes; MERGE on business keys.
4. Lint snippets with `python3 plugins/graph-engineering/scripts/lint_graph_shape.py`.

## Guardrails

- Advisory only. No live database. Date any engine claim.
- See [`../skills/model-property-graph/SKILL.md`](../skills/model-property-graph/SKILL.md).
