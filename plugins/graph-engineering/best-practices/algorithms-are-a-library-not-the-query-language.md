# Algorithms are a library, not the query language

**Status:** Pattern (strong default)
**Domain:** Graph algorithms
**Applies to:** `graph-engineering`

---

## Why this exists

Pathfinding, centrality, and community detection are **library** work (Neo4j GDS, cuGraph, NetworkX on a projected subgraph). They are not Cypher or GQL features you should invent as `CALL algo.*`. Mixing them into the query language hides the projection step and the cost model.

## How to apply

1. Write a **bounded, typed** traversal (or an explicit subgraph projection).
2. Run the algorithm in the library the engine actually ships.
3. Write the hop-limit / weight property as library parameters, not as `-[*]->`.

## Edge cases / when the rule does NOT apply

- A 1–2 hop neighborhood is a traversal, not an algorithm.
- Shortest-path as a single built-in (`shortestPath`, GQL equivalent) is still a library-shaped call — name the function the engine documents, `[verify-at-use]`.

## See also

- [`../knowledge/graph-languages-and-engines-2026.md`](../knowledge/graph-languages-and-engines-2026.md)

## Provenance

House opinion #6 (C30).

---

_Last reviewed: 2026-08-14_
