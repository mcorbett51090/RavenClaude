# Graph languages and engines — 2026 map

**Last reviewed:** 2026-08-14
Every volatile row is `[verify-at-use]`. Re-fetch official docs before quoting a version, GA word, or SKU to a client.

## Languages

| Language | What it is | Teach when |
|---|---|---|
| **ISO/IEC 39075:2024 GQL** | Published International Standard for property-graph data structures and basic operations. Status 90.92 (to be revised); Cor 1:2026 published. | Name it as **the standard**. |
| **Cypher / openCypher** | Vendor-born LPG language (Neo4j). openCypher’s mission after 2024-04-11 is to help implementors evolve toward GQL. | **Teach first.** Clients type Cypher. |
| **Gremlin** | Apache TinkerPop traversal language (imperative). | Existing TinkerPop / Cosmos Gremlin / Neptune Gremlin workloads. |
| **SPARQL 1.1** | W3C RDF query language. **Do not date SPARQL 1.2 / RDF 1.2** — not fetched this session. | RDF / shared-IRI / entailment branch. |

GQL is the standard. Cypher is the lingua franca. The slash command is `/write-graph-query`, **not** `/write-gql`.

Pre-GQL Cypher `*` quantified paths are **not** GQL. The linter WARNINGs a `*` inside a `.gql` file.

## Engines (existence + fetched facts)

| Engine | Fetched fact (2026-08-14) | Notes |
|---|---|---|
| **Neo4j** | LPG + Cypher; Graph Data Science is a **library**, not the query language (C30). | Default client dialect, not the only engine. |
| **Amazon Neptune** | Multi-language: Gremlin + openCypher + SPARQL (C24). | Pick the language from the data model, not the brand. |
| **Microsoft Fabric Graph** | Labeled property graph over OneLake; GQL / NL2GQL. Marketplace file dates **GA (June 2026)**; Learn overview fetched this session did not independently confirm the GA word. `[verify-at-use]` (C11, C25). | SKU / CU / OneLake stay in `microsoft-fabric`. Craft stays here. |
| **Google Spanner Graph** | GQL on Spanner. Enterprise / Enterprise Plus. No PostgreSQL interface for the graph (C26). `[verify-at-use]` | Graph-over-tables projection — the allowed alternative to dual-write. |
| **Azure Cosmos DB Gremlin API** | Gremlin API exists; current docs steer OLAP / some migrations toward Fabric Graph (C27). `[verify-at-use]` | Do not present Cosmos Gremlin as the 2026 default OLAP graph. |
| **Apache AGE** | Postgres extension, Cypher-in-SQL. Named in the field. `[verify-at-use]` | |
| **FalkorDB** | Redis-heritage LPG. Named in the field. `[verify-at-use]` | |
| **JanusGraph** | TinkerPop / Gremlin. Named in the field. `[verify-at-use]` | |
| **Kuzu** | **Archived 2025-10-10.** Do **not** teach as the 2026 embedded default (C28). | Cite only as a cautionary archived example. |

**Omitted / unverified this session:** TigerGraph; Memgraph intro URL 404. `[unverified — not fetched 2026-08-14]`

## Algorithm libraries are not languages

Pathfinding, centrality, and community detection belong in a **library** (Neo4j GDS, cuGraph, NetworkX on a projection). Do not invent `CALL algo.pageRank` as if it were Cypher or GQL.

## See also

- [`../best-practices/gql-is-the-standard-cypher-is-the-lingua-franca.md`](../best-practices/gql-is-the-standard-cypher-is-the-lingua-franca.md)
- [`../best-practices/algorithms-are-a-library-not-the-query-language.md`](../best-practices/algorithms-are-a-library-not-the-query-language.md)

## Sources

- ISO 39075:2024 — https://www.iso.org/standard/76120.html (retrieved 2026-08-14) (C15).
- openCypher — https://opencypher.org/ (retrieved 2026-08-14) (C16).
- W3C RDF 1.1 Primer — https://www.w3.org/TR/rdf11-primer/ (retrieved 2026-08-14) (C17, C18).
- Marketplace `plugins/microsoft-fabric/knowledge/fabric-2026-capability-map.md:29` (C11).
