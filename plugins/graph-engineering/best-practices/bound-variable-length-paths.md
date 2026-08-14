# Bound every variable-length path

**Status:** Absolute rule
**Domain:** Traversal queries
**Applies to:** `graph-engineering`

---

## Why this exists

An unbounded Cypher `-[*]->` (or `-[*..]->`, `-[*1..]->`) or GQL `{1,}` with no upper bound is a latency bomb. The planner cannot cap expansion; a single dense node turns the query into a graph-wide search. The hook and linter flag this.

## How to apply

```cypher
MATCH (a:Person)-[:KNOWS*1..3]->(b:Person) RETURN b
```

The unbounded star form (no upper hop) is the defect — see `scripts/fixtures/bad_unbounded.cypher`.

In GQL use `{1, 3}`, not `{1,}`.

**Do:** pick a domain-honest upper bound (reporting line, BOM depth, fraud-hop policy).

**Don't:** ship `*` “and add a LIMIT later” — `LIMIT` does not stop expansion on all engines.

## Edge cases / when the rule does NOT apply

- Fixed-length `[:KNOWS]` (no `*`) needs no bound.
- Algorithm libraries that take a hop-limit parameter are not query-language `*`.

## See also

- [`../scripts/lint_graph_shape.py`](../scripts/lint_graph_shape.py)
- [`../knowledge/graph-languages-and-engines-2026.md`](../knowledge/graph-languages-and-engines-2026.md)

## Provenance

Codifies house opinion #3 in [`../CLAUDE.md`](../CLAUDE.md). Path-cost is documented engine behavior (C20), not a worktree repro.

---

_Last reviewed: 2026-08-14_
