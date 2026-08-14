# Type every relationship

**Status:** Absolute rule
**Domain:** Property-graph modeling
**Applies to:** `graph-engineering`

---

## Why this exists

A relationship in a labeled property graph **must** have a type and a direction. Untyped `()-[]-()` (or `-[]->`) throws away the only thing that makes a traversal cheaper than a join: knowing *which* edge to walk. The store cannot index “any edge.” The hook and `lint_graph_shape.py` flag this.

## How to apply

```cypher
MATCH (a:Person)-[:KNOWS]->(b:Person) RETURN b
```

The empty-bracket form (no type between the square brackets) is the defect — see `scripts/fixtures/bad_untyped.cypher`.

**Do:** name the type; keep the direction; put link payload on the relationship.

**Don't:** leave the type blank “until we know”; invent a pair of inverse types without a reason.

## Edge cases / when the rule does NOT apply

- RDF/SPARQL uses predicates (IRIs), not LPG relationship types — still type the predicate; do not emit `-[]-`.
- Exploratory `CALL db.schema` / catalog queries are not instance traversals.

## See also

- [`../knowledge/lpg-modeling-catalog.md`](../knowledge/lpg-modeling-catalog.md)
- [`../hooks/flag-graph-smells.sh`](../hooks/flag-graph-smells.sh)

## Provenance

Codifies house opinion #2 in [`../CLAUDE.md`](../CLAUDE.md). Grounded in the LPG model (C17, C29).

---

_Last reviewed: 2026-08-14_
