# GQL is the standard; Cypher is the lingua franca

**Status:** Pattern (strong default)
**Domain:** Query-language teaching
**Applies to:** `graph-engineering`

---

## Why this exists

ISO/IEC 39075:2024 GQL is the published property-graph standard. Clients still type **Cypher**. A plugin that teaches only Neo4j Cypher, or only GQL, will mis-route half of 2026 work. Teach Cypher first, name GQL as the standard, keep Gremlin and SPARQL 1.1 in the field.

## How to apply

- Slash command: `/write-graph-query`, **not** `/write-gql`.
- Examples: Cypher first, then a GQL equivalent when the engine is GQL-native (Fabric Graph, Spanner Graph).
- SPARQL for the RDF branch; Gremlin for TinkerPop / Cosmos Gremlin / Neptune Gremlin.

## Edge cases / when the rule does NOT apply

- A client whose engine is SPARQL-only should not be shown Cypher first — start at SPARQL.
- Do not invent SPARQL 1.2 / RDF 1.2 support.

## See also

- [`../knowledge/graph-languages-and-engines-2026.md`](../knowledge/graph-languages-and-engines-2026.md)

## Provenance

House opinion #5. C15 (ISO GQL), C16 (openCypher → GQL).

---

_Last reviewed: 2026-08-14_
